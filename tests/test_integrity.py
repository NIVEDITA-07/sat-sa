import unittest
import os
import tempfile
import json
import shutil
import hashlib

from engine.integrity import (
    get_file_sha256,
    capture_assessment_integrity,
    verify_assessment_integrity,
    get_manifest_path
)

class TestSATSAIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file1_path = os.path.join(self.temp_dir, "test1.csv")
        self.file2_path = os.path.join(self.temp_dir, "test2.csv")
        
        with open(self.file1_path, "wb") as f:
            f.write(b"id,value\n1,A\n")
        
        with open(self.file2_path, "wb") as f:
            f.write(b"id,value\n2,B\n")
            
        self.files_map = {
            "test1.csv": self.file1_path,
            "test2.csv": self.file2_path
        }
        
        # Override the manifest directory for testing
        self.original_get_manifest_path = get_manifest_path
        import engine.integrity
        engine.integrity.get_manifest_path = lambda aid: os.path.join(self.temp_dir, f"{aid}_manifest.json")

    def tearDown(self):
        import engine.integrity
        engine.integrity.get_manifest_path = self.original_get_manifest_path
        shutil.rmtree(self.temp_dir)

    def test_deterministic_hash(self):
        # TEST 1: Same source content -> same hash
        hash1 = get_file_sha256(self.file1_path)
        hash2 = get_file_sha256(self.file1_path)
        self.assertEqual(hash1, hash2)

    def test_different_content(self):
        # TEST 2: Different content -> different hash
        hash1 = get_file_sha256(self.file1_path)
        hash2 = get_file_sha256(self.file2_path)
        self.assertNotEqual(hash1, hash2)

    def test_known_source_artifact(self):
        # TEST 3: Known source artifact
        expected_hash = hashlib.sha256(b"id,value\n1,A\n").hexdigest()
        self.assertEqual(get_file_sha256(self.file1_path), expected_hash)

    def test_manifest_creation(self):
        # TEST 4: Manifest creation
        aid = "TEST-ASSESSMENT-001"
        manifest = capture_assessment_integrity(aid, self.files_map)
        
        self.assertEqual(manifest.assessment_id, aid)
        self.assertEqual(manifest.hash_algorithm, "SHA-256")
        self.assertEqual(len(manifest.source_artifacts), 2)
        
        manifest_path = os.path.join(self.temp_dir, f"{aid}_manifest.json")
        self.assertTrue(os.path.exists(manifest_path))

    def test_successful_verification(self):
        # TEST 5: Successful verification
        aid = "TEST-ASSESSMENT-002"
        capture_assessment_integrity(aid, self.files_map)
        
        result = verify_assessment_integrity(aid, self.files_map)
        self.assertEqual(result.overall_status, "UNCHANGED")
        self.assertEqual(result.unchanged_count, 2)
        self.assertEqual(result.changed_count, 0)

    def test_modified_source(self):
        # TEST 6: Modified source
        aid = "TEST-ASSESSMENT-003"
        capture_assessment_integrity(aid, self.files_map)
        
        # Modify the source file
        with open(self.file1_path, "a") as f:
            f.write("3,C\n")
            
        result = verify_assessment_integrity(aid, self.files_map)
        self.assertEqual(result.overall_status, "CHANGED")
        self.assertEqual(result.changed_count, 1)
        self.assertEqual(result.unchanged_count, 1)
        
        # Check specific artifact
        artifact = next(a for a in result.artifact_results if a.source_name == "test1.csv")
        self.assertEqual(artifact.status, "CHANGED")

    def test_missing_source(self):
        # TEST 7: Missing source
        aid = "TEST-ASSESSMENT-004"
        capture_assessment_integrity(aid, self.files_map)
        
        # Remove a file
        os.remove(self.file1_path)
        
        result = verify_assessment_integrity(aid, self.files_map)
        self.assertEqual(result.overall_status, "MISSING")
        self.assertEqual(result.missing_count, 1)
        
        artifact = next(a for a in result.artifact_results if a.source_name == "test1.csv")
        self.assertEqual(artifact.status, "MISSING")
        
    def test_unavailable_evidence(self):
        # TEST 8: Unavailable evidence (path not provided in current_files_map)
        aid = "TEST-ASSESSMENT-005"
        capture_assessment_integrity(aid, self.files_map)
        
        # Pass a map missing one of the files
        incomplete_map = {"test2.csv": self.file2_path}
        
        result = verify_assessment_integrity(aid, incomplete_map)
        self.assertEqual(result.overall_status, "UNAVAILABLE")
        self.assertEqual(result.unavailable_count, 1)

    def test_original_source_untouched(self):
        # TEST 9: Original source remains untouched
        import stat
        aid = "TEST-ASSESSMENT-006"
        
        # Capture the original modification time
        original_mtime = os.stat(self.file1_path).st_mtime
        with open(self.file1_path, "rb") as f:
            original_content = f.read()
        
        capture_assessment_integrity(aid, self.files_map)
        verify_assessment_integrity(aid, self.files_map)
        
        new_mtime = os.stat(self.file1_path).st_mtime
        with open(self.file1_path, "rb") as f:
            new_content = f.read()
        
        self.assertEqual(original_mtime, new_mtime)
        self.assertEqual(original_content, new_content)
