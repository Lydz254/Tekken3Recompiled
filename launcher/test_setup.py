"""ROM-free checks for setup integrity, archive boundaries and cancellation."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,unittest,zipfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import setup_backend as backend
from easy_launcher import ProcessJob

class SetupTests(unittest.TestCase):
    def test_archive_traversal_rejected_before_any_write(self):
        for name in ('../escape','C:/escape','safe/../../escape','safe\\..\\..\\escape','file:stream'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);archive=root/'bad.zip'
                with zipfile.ZipFile(archive,'w') as z:z.writestr('good','okay');z.writestr(name,'bad')
                with self.assertRaises(backend.SetupError):backend.safe_extract(archive,root/'out')
                self.assertFalse((root/'out/good').exists())

    def test_valid_archive_and_case_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);archive=root/'tools.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('bin/','');z.writestr('bin/tool.exe','synthetic')
            backend.safe_extract(archive,root/'out')
            self.assertEqual((root/'out/bin/tool.exe').read_text(),'synthetic')
            with zipfile.ZipFile(archive,'w') as z:z.writestr('A','1');z.writestr('a','2')
            with self.assertRaises(backend.SetupError):backend.safe_extract(archive,root/'bad')

    def test_cached_tool_requires_its_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'downloads').mkdir();path=root/'downloads/tool.zip';path.write_bytes(b'tool')
            spec={'filename':'tool.zip','sha256':hashlib.sha256(b'tool').hexdigest(),'url':'https://invalid.example/tool.zip','size':4}
            with patch.object(backend,'STATE',root),patch.object(backend.urllib.request,'urlopen',side_effect=OSError('offline')) as network:
                self.assertEqual(backend.download(spec),path);network.assert_not_called()
                path.write_bytes(b'bad')
                with self.assertRaises(backend.SetupError):backend.download(spec)
                network.assert_called_once()

    def test_missing_or_changed_game_is_not_marked_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);exe=root/'build/game.exe';exe.parent.mkdir();exe.write_bytes(b'game')
            (root/'disc').mkdir();(root/'disc/Tekken 3 (USA).cue').write_text('synthetic')
            state=root/'.setup';backend.save_json(state/'ready.json',{'release':backend.RELEASE,'jun':False,'exe_sha256':backend.digest(exe)})
            with patch.object(backend,'ROOT',root),patch.object(backend,'STATE',state),patch.object(backend,'EXE',exe):
                self.assertTrue(backend.ready());exe.write_bytes(b'changed');self.assertFalse(backend.ready())

    @unittest.skipUnless(os.name=='nt','Windows process ownership')
    def test_cancel_closes_owned_worker(self):
        job=ProcessJob()
        child=subprocess.Popen([sys.executable,'-c','import sys,time;sys.stdin.readline();time.sleep(120)'],stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job.assign(child);child.stdin.write(b'START\n');child.stdin.flush()
            job.close();self.assertIsNotNone(child.wait(timeout=5))
        finally:
            job.close();child.stdin.close()
            if child.poll() is None:child.terminate();child.wait()

if __name__=='__main__':unittest.main()
