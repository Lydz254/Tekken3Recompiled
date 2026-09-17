cmake_minimum_required(VERSION 3.20)
project(Tekken3Recomp LANGUAGES C CXX)

set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH
    "Path to psxrecomp")

# --- Opt-in product surfaces (OFF by default in the framework) -------------
# Scaffold prompts / flags fill these. Without recomp-ui, PSX_RECOMP_UI is OFF.
# Setup-host CI requires WIZARD_CMAKE_BLOCK / ENABLE_SETUP_WIZARD (FORCE_SETUP_HOST
# alone does not open first-run / Generate & rebuild).
# recomp-ui submodule present (PSX_RECOMP_UI defaults ON).
# Full netplay UI — enable after adding recomp-ui + testing:
# if(EXISTS "${PSXRECOMP_ROOT}/lib/recomp-net/CMakeLists.txt")
#     set(PSX_NETPLAY ON CACHE BOOL "…" FORCE)
# endif()
set(PSX_SETUP_WIZARD ON CACHE BOOL
    "Advertise first-run setup wizard + Generate & rebuild in recomp-ui" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

option(TEKKEN3_BUILD_RECOMP_RUNTIME
    "Build the legacy hybrid recompilation/reference executable" ON)
if(TEKKEN3_BUILD_RECOMP_RUNTIME)
psxrecomp_add_game_runtime(psx-runtime
    # ENABLE_NETPLAY_IF_PRESENT
    # NETPLAY_LOBBY_URL "ws://netplay.retcomm.net:8765"
    ENABLE_SETUP_WIZARD
    WINDOW_TITLE "Tekken 3 Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    # LAUNCHER_BOXART "${CMAKE_CURRENT_SOURCE_DIR}/launcher_assets/img/boxart.tga"
    GEN_MARKER "generated/SLUS_004.02_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_004.02_full_*.c"
    CODEGEN_SETUP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/codegen_setup.c"
)

# Game-owned visual enhancements are trusted static plugins.  Package
# manifests can select them, but never load native code from an archive.
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/generated/SLUS_004.02_dispatch.c"
   AND NOT PSXRECOMP_FORCE_SETUP_HOST)
target_sources(psx-runtime PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_widescreen_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_fight_camera.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_forest_hd_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_nina_skin_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_xiaoyu_skin_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_anna_skin_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_kuma_skin_mod.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_unlock_characters_mod.c"
)

# Rebuild a narrow native camera variant from the current generated routine.
# Exact MIPS/operand guards keep this reproducible without editing guest RAM
# or maintaining a second hand-copied recompiler output file.
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(TEKKEN3_FIGHT_CAMERA_SOURCE "${CMAKE_CURRENT_BINARY_DIR}/tekken3_fight_camera_generated.c")
add_custom_target(tekken3_fight_camera_codegen
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/build_fight_camera.py"
        --source "${CMAKE_CURRENT_SOURCE_DIR}/generated/SLUS_004.02_full_26.c"
        --exe "${CMAKE_CURRENT_SOURCE_DIR}/disc/SLUS_004.02"
        --output "${TEKKEN3_FIGHT_CAMERA_SOURCE}"
    BYPRODUCTS "${TEKKEN3_FIGHT_CAMERA_SOURCE}"
    VERBATIM)
add_dependencies(psx-runtime tekken3_fight_camera_codegen)
target_sources(psx-runtime PRIVATE "${TEKKEN3_FIGHT_CAMERA_SOURCE}")
target_include_directories(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")
set_source_files_properties("${TEKKEN3_FIGHT_CAMERA_SOURCE}" PROPERTIES
    INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}/generated")
# Apple's ld64 has no --wrap, and the option is a hard error there, so every
# wrapped routine below is redirected with the preprocessor instead: the
# defining TU is compiled with -D<sym>=__real_<sym> and the wrapping TU with
# -D__wrap_<sym>=<sym>. Call sites elsewhere still say <sym> and therefore
# reach the wrapper, which is what --wrap does, and a wrapper delegating to
# __real_<sym> still finds the stock routine. Every other platform keeps the
# linker option. WRAPPER names a generated wrapper that cannot be found by
# scanning src/; DEFINED_IN overrides a defining TU that is not compiled.
function(tekken3_wrap_symbol sym)
    cmake_parse_arguments(TW "" "WRAPPER;DEFINED_IN" "" ${ARGN})
    if(NOT APPLE)
        target_link_options(psx-runtime PRIVATE "-Wl,--wrap=${sym}")
        return()
    endif()
    set_property(GLOBAL APPEND PROPERTY TEKKEN3_WRAP_SYMS "${sym}")
    if(TW_WRAPPER)
        set_property(GLOBAL PROPERTY TEKKEN3_WRAP_WRAPPER_${sym} "${TW_WRAPPER}")
    endif()
    if(TW_DEFINED_IN)
        set_property(GLOBAL PROPERTY TEKKEN3_WRAP_DEF_${sym} "${TW_DEFINED_IN}")
    endif()
endfunction()

# Resolve every accumulated symbol in one pass and apply the definitions.
function(tekken3_apply_wraps)
    if(NOT APPLE)
        return()
    endif()
    get_property(_syms GLOBAL PROPERTY TEKKEN3_WRAP_SYMS)
    if(NOT _syms)
        return()
    endif()
    string(REPLACE ";" "," _symarg "${_syms}")
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
                "${CMAKE_CURRENT_SOURCE_DIR}/tools/resolve_wrap_targets.py"
                --root "${CMAKE_CURRENT_SOURCE_DIR}" --symbols "${_symarg}"
        OUTPUT_VARIABLE _out ERROR_VARIABLE _err RESULT_VARIABLE _rc
        OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(NOT _rc EQUAL 0)
        message(FATAL_ERROR
            "resolve_wrap_targets.py failed (exit ${_rc}); --wrap emulation "
            "cannot be applied:\n${_err}")
    endif()
    string(REPLACE "\n" ";" _lines "${_out}")
    foreach(_line IN LISTS _lines)
        string(REPLACE "|" ";" _parts "${_line}")
        list(GET _parts 0 _sym)
        list(GET _parts 1 _def)
        set(_wrapper "")
        list(LENGTH _parts _n)
        if(_n GREATER 2)
            list(GET _parts 2 _wrapper)
        endif()
        get_property(_def_override GLOBAL PROPERTY TEKKEN3_WRAP_DEF_${_sym})
        if(_def_override)
            set(_def "${_def_override}")
        endif()
        get_property(_wrapper_override GLOBAL PROPERTY TEKKEN3_WRAP_WRAPPER_${_sym})
        if(_wrapper_override)
            set(_wrapper "${_wrapper_override}")
        endif()
        if(NOT _wrapper)
            message(FATAL_ERROR
                "no wrapper found for ${_sym}: it is defined in ${_def} but no "
                "src/*.c defines __wrap_${_sym}. Pass WRAPPER to "
                "tekken3_wrap_symbol() when a generated file wraps it.")
        endif()
        set_property(SOURCE "${_def}" APPEND PROPERTY
            COMPILE_DEFINITIONS "${_sym}=__real_${_sym}")
        set_property(SOURCE "${_wrapper}" APPEND PROPERTY
            COMPILE_DEFINITIONS "__wrap_${_sym}=${_sym}")
    endforeach()
    list(LENGTH _syms _count)
    message(STATUS "Emulated -Wl,--wrap for ${_count} symbol(s) without ld64")
endfunction()

# Apple's ld64 has no --wrap, and the option is a hard error there. The
# regenerated camera variant is a complete replacement: build_fight_camera.py
# renames the stock definition to __wrap_func_80064E10, nothing calls
# __real_func_80064E10, and every reference lives in the dispatch table. So
# reproduce --wrap with the preprocessor: move the stock definition aside in
# its own shard, and let the variant take the name the call sites use. Other
# platforms keep the linker option.
tekken3_wrap_symbol(func_80064E10 WRAPPER "${TEKKEN3_FIGHT_CAMERA_SOURCE}")
set_property(TARGET psx-runtime APPEND PROPERTY LINK_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded/packages/tekken3.enhancement.true-widescreen/1.0.0/manifest.toml"
    "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded/packages/tekken3.enhancement.true-widescreen/1.0.0/README.md")

# A fresh installation enables Jun after the user imports the donor assets.
set(_tekken3_jun_default OFF)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/workspace/jun-import/jun/Jun-TTT1-combat.jmv")
    set(_tekken3_jun_default ON)
endif()
option(TEKKEN3_JUN_EXPERIMENTAL "Build the Jun character import" ${_tekken3_jun_default})
if(TEKKEN3_JUN_EXPERIMENTAL)
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_mod.c")
    set(JUN_GENERATED_DIR "${CMAKE_CURRENT_SOURCE_DIR}/workspace/jun-import/generated")
    if(NOT EXISTS "${JUN_GENERATED_DIR}/jun-render.exe_full_00.c")
        message(FATAL_ERROR "Prepare the local Jun assets with tools/prepare_jun_import.py first")
    endif()
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_renderer.c")
    target_include_directories(psx-runtime PRIVATE "${JUN_GENERATED_DIR}")
    tekken3_wrap_symbol(func_80036CAC)
    tekken3_wrap_symbol(func_80035BC0)
    tekken3_wrap_symbol(func_80035190)
    tekken3_wrap_symbol(func_80035CE8)
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_motion.c")
    tekken3_wrap_symbol(func_8003AD10)
    tekken3_wrap_symbol(func_80037CBC)
    tekken3_wrap_symbol(func_8006A3BC)
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_combat.c")
    set(JUN_COMBAT_HOOKS "${CMAKE_CURRENT_BINARY_DIR}/tekken3_jun_combat_generated.c")
    set(JUN_PUSH_HOOKS "${CMAKE_CURRENT_BINARY_DIR}/tekken3_jun_push_generated.c")
    add_custom_target(tekken3_jun_combat_codegen
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/build_jun_combat_hooks.py"
            --root "${CMAKE_CURRENT_SOURCE_DIR}" --output "${JUN_COMBAT_HOOKS}"
        BYPRODUCTS "${JUN_COMBAT_HOOKS}" "${JUN_PUSH_HOOKS}" VERBATIM)
    add_dependencies(psx-runtime tekken3_jun_combat_codegen)
    target_sources(psx-runtime PRIVATE "${JUN_COMBAT_HOOKS}" "${JUN_PUSH_HOOKS}")
    set_source_files_properties("${CMAKE_CURRENT_SOURCE_DIR}/generated/SLUS_004.02_full_04.c" PROPERTIES HEADER_FILE_ONLY TRUE)
    set_source_files_properties("${JUN_COMBAT_HOOKS}" "${JUN_PUSH_HOOKS}" PROPERTIES
        INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}/generated")
    tekken3_wrap_symbol(func_8002F3AC WRAPPER "${JUN_COMBAT_HOOKS}")
    tekken3_wrap_symbol(func_8003F098 WRAPPER "${JUN_COMBAT_HOOKS}")
    tekken3_wrap_symbol(func_8002DE24 WRAPPER "${JUN_COMBAT_HOOKS}")
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_voices.c")
    tekken3_wrap_symbol(func_80040C90)
    tekken3_wrap_symbol(spu_render)
    tekken3_wrap_symbol(spu_set_host_mix_volume)
    tekken3_wrap_symbol(spu_init)
    tekken3_wrap_symbol(spu_snapshot_read)
    tekken3_wrap_symbol(func_8002D178)
    tekken3_wrap_symbol(func_80038B4C)
    tekken3_wrap_symbol(func_800389C0)
    tekken3_wrap_symbol(func_8002D264)
    tekken3_wrap_symbol(func_8002E8D0)
    tekken3_wrap_symbol(func_8002E0BC)
    tekken3_wrap_symbol(func_8002CC28)
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_selector.c")
    tekken3_wrap_symbol(tekken3_outfits_input)
    tekken3_wrap_symbol(host_osd_outfit_image)
    tekken3_wrap_symbol(host_osd_draw_sdl)
    target_sources(psx-runtime PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/tekken3_jun_roster.c")
    tekken3_wrap_symbol(func_80052938)
    tekken3_wrap_symbol(func_80052940)
    tekken3_wrap_symbol(func_8004B790)
    tekken3_wrap_symbol(func_8004B928)
    # Shard 04 is HEADER_FILE_ONLY here; JUN_PUSH_HOOKS compiles its copy.
    tekken3_wrap_symbol(func_80031BFC DEFINED_IN "${JUN_PUSH_HOOKS}")
    tekken3_wrap_symbol(func_80052AD0)
    tekken3_wrap_symbol(func_80052958)
    tekken3_wrap_symbol(func_80052990)
    tekken3_wrap_symbol(func_8006BF20)
    tekken3_wrap_symbol(func_8003626C)
    tekken3_wrap_symbol(func_80036294)
    tekken3_wrap_symbol(func_800362C4)
    tekken3_wrap_symbol(func_8003F044)
endif()

tekken3_apply_wraps()

# A dynamic developer build can import the bundled Clang C++ runtime.  Stage it
# when that actually happens; production builds use PSX_STATIC_RUNTIME and need
# no non-system DLLs beside the executable.
if(WIN32 AND NOT PSX_STATIC_RUNTIME)
    get_filename_component(_tekken3_compiler_bin "${CMAKE_CXX_COMPILER}" DIRECTORY)
    foreach(_tekken3_runtime_dll IN ITEMS libc++.dll libunwind.dll)
        if(EXISTS "${_tekken3_compiler_bin}/${_tekken3_runtime_dll}")
            add_custom_command(TARGET psx-runtime POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_tekken3_compiler_bin}/${_tekken3_runtime_dll}"
                    "$<TARGET_FILE_DIR:psx-runtime>/${_tekken3_runtime_dll}"
                VERBATIM
            )
        endif()
    endforeach()
elseif(WIN32)
    add_custom_command(TARGET psx-runtime POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E rm -f
            "$<TARGET_FILE_DIR:psx-runtime>/libc++.dll"
            "$<TARGET_FILE_DIR:psx-runtime>/libunwind.dll"
        VERBATIM
    )
endif()

# Stage the reviewed Tekken-specific catalog after the framework catalog.  The
# framework's own POST_BUILD step recreates mods/, so ordering this command
# here preserves both catalogs and also removes stale game packages.
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E rm -rf
        "$<TARGET_FILE_DIR:psx-runtime>/mods/packages/tekken3.enhancement.true-widescreen"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded/packages"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/packages"
    COMMENT "Staging Tekken 3 built-in mod catalog"
    VERBATIM
)
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/forest-hd"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/forest-hd"
    COMMENT "Staging forest HD texture assets"
    VERBATIM
)
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/nina-white-satin"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/nina-white-satin"
    COMMENT "Staging Nina White Satin textures"
    VERBATIM
)
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/xiaoyu-cherry-blossom"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/xiaoyu-cherry-blossom"
    COMMENT "Staging Xiaoyu Cherry Blossom Ribbon textures"
    VERBATIM
)
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/anna-jessica-rabbit"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/anna-jessica-rabbit"
    COMMENT "Staging Anna Jessica Rabbit textures"
    VERBATIM
)
file(GLOB TEKKEN3_GALLERY_ASSETS CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/outfit-menu/*")
file(GLOB TEKKEN3_KUMA_ASSETS CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/kuma-polar-bear/*")
set_property(TARGET psx-runtime APPEND PROPERTY LINK_DEPENDS ${TEKKEN3_KUMA_ASSETS}
    "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded/packages/tekken3.skin.kuma-polar-bear/1.0.0/manifest.toml")
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/kuma-polar-bear"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/kuma-polar-bear"
    COMMENT "Staging Kuma Polar Bear textures"
    VERBATIM)
set_property(TARGET psx-runtime APPEND PROPERTY LINK_DEPENDS ${TEKKEN3_GALLERY_ASSETS})
add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_CURRENT_SOURCE_DIR}/mods/assets/outfit-menu"
        "$<TARGET_FILE_DIR:psx-runtime>/mods/outfit-menu"
    COMMENT "Staging skin gallery artwork and catalog"
    VERBATIM
)

# Local imports also work in the normal recomp launch. Keep the original ROM
# dumps and generated packs private; stage only the nine runtime artifacts.
if(TEKKEN3_JUN_EXPERIMENTAL)
    set(JUN_RUNTIME_FILES
        Jun-TTT1-arcade-P1.3dm Jun-TTT1-arcade-P1.relocs Jun-TTT1-arcade-P1.tim
        Jun-TTT1-idle.poses Jun-TTT1-combat.jmv Jun-TTT1-tables.jst Jun-TTT1-voices.juv
        Jun-T3-ui.jui Jun-T3-name.4bpp)
    set(JUN_RUNTIME_ASSETS)
    foreach(JUN_FILE IN LISTS JUN_RUNTIME_FILES)
        list(APPEND JUN_RUNTIME_ASSETS "${CMAKE_CURRENT_SOURCE_DIR}/workspace/jun-import/jun/${JUN_FILE}")
    endforeach()
    set(JUN_PACKAGE "${CMAKE_CURRENT_SOURCE_DIR}/mods/local-packages/tekken3.character.jun-probe/1.0.0/manifest.toml")
    set_property(TARGET psx-runtime APPEND PROPERTY LINK_DEPENDS ${JUN_RUNTIME_ASSETS} "${JUN_PACKAGE}")
    add_custom_command(TARGET psx-runtime POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "$<TARGET_FILE_DIR:psx-runtime>/mods/jun"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${JUN_RUNTIME_ASSETS} "$<TARGET_FILE_DIR:psx-runtime>/mods/jun"
        COMMAND ${CMAKE_COMMAND} -E make_directory "$<TARGET_FILE_DIR:psx-runtime>/mods/packages/tekken3.character.jun-probe/1.0.0"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${JUN_PACKAGE}" "$<TARGET_FILE_DIR:psx-runtime>/mods/packages/tekken3.character.jun-probe/1.0.0/manifest.toml"
        COMMENT "Staging private Jun character for the normal recomp launch"
        VERBATIM)
endif()

endif()

endif() # Full game enhancements need locally generated game code.

# The recompiled executable above remains a behavioral oracle while the game is
# migrated system-by-system.  The PC-port target below is deliberately separate:
# it does not compile generated guest code, OpenBIOS, the PS1 GPU/GTE, or the
# compatibility scheduler.
option(TEKKEN3_BUILD_PC_PORT "Build the independent native Tekken 3 PC port" OFF)
if(TEKKEN3_BUILD_PC_PORT)
    add_subdirectory(native)
endif()
