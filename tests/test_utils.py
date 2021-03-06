
import kindred
import os
import shutil
import tempfile
import hashlib

def test_loadBioNLP_findDir():
	tempDir = tempfile.mkdtemp()
	actualDirPath = os.path.join(tempDir,'actualDir')
	os.mkdir(actualDirPath)
	assert kindred.utils._findDir('actualDir',tempDir) == actualDirPath
	assert kindred.utils._findDir('doesntExist',tempDir) == None
	shutil.rmtree(tempDir)

def test_corruptFileInWayOfDownload():
	tempDir = tempfile.mkdtemp()

	fileInfo = ('https://github.com/jakelever/kindred/archive/1.0.tar.gz','1.0.tar.gz','363d36269a6ea83e1a253a0709dc365c3536ecd2976096ea0600cd4ef2f1e33c')

	expectedDownloadPath = os.path.join(tempDir,fileInfo[1])
	with open(expectedDownloadPath,'w') as f:
		f.write("\n".join(map(str,range(100))))

	oldSHA256 = hashlib.sha256(open(expectedDownloadPath, 'rb').read()).hexdigest()

	kindred.utils._downloadFiles([fileInfo],tempDir)

	newSHA256 = hashlib.sha256(open(expectedDownloadPath, 'rb').read()).hexdigest()

	assert oldSHA256 != newSHA256
	assert newSHA256 == fileInfo[2]

	shutil.rmtree(tempDir)
