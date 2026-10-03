import hashlib
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

@dataclass
class ArtifactIntegrity:
    source_name: str
    source_type: str
    sha256: str
    captured_at: str
    record_count: Optional[int] = None

@dataclass
class IntegrityManifest:
    assessment_id: str
    manifest_version: str
    created_at: str
    hash_algorithm: str
    engine_version: str
    configuration_version: str
    source_artifacts: List[ArtifactIntegrity]

@dataclass
class ArtifactVerificationResult:
    source_name: str
    expected_hash: str
    current_hash: Optional[str]
    status: str  # UNCHANGED, CHANGED, MISSING, UNAVAILABLE
    reason: Optional[str]

@dataclass
class IntegrityVerificationResult:
    assessment_id: str
    overall_status: str  # UNCHANGED, CHANGED, MISSING, UNAVAILABLE, ERROR
    verified_at: str
    artifacts_checked: int
    unchanged_count: int
    changed_count: int
    missing_count: int
    unavailable_count: int
    artifact_results: List[ArtifactVerificationResult]

def get_file_sha256(filepath: str) -> str:
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_manifest_path(assessment_id: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_dir = os.path.join(base_dir, "data", "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    return os.path.join(manifest_dir, f"{assessment_id}_manifest.json")

def capture_assessment_integrity(assessment_id: str, files_map: Dict[str, str], engine_version: str = "1.0", config_version: str = "1.0") -> IntegrityManifest:
    """
    Captures the integrity of the source files and creates a manifest.
    files_map is a dictionary mapping source_name -> filepath.
    """
    artifacts = []
    now = datetime.now(timezone.utc).isoformat()
    
    for source_name, filepath in files_map.items():
        if os.path.exists(filepath):
            file_hash = get_file_sha256(filepath)
            artifacts.append(ArtifactIntegrity(
                source_name=source_name,
                source_type="csv",
                sha256=file_hash,
                captured_at=now
            ))
            
    manifest = IntegrityManifest(
        assessment_id=assessment_id,
        manifest_version="1.0",
        created_at=now,
        hash_algorithm="SHA-256",
        engine_version=engine_version,
        configuration_version=config_version,
        source_artifacts=artifacts
    )
    
    # Save to disk
    manifest_path = get_manifest_path(assessment_id)
    with open(manifest_path, "w") as f:
        json.dump(asdict(manifest), f, indent=2)
        
    return manifest

def verify_assessment_integrity(assessment_id: str, current_files_map: Dict[str, str]) -> IntegrityVerificationResult:
    """
    Verifies the integrity of an assessment against its manifest.
    """
    manifest_path = get_manifest_path(assessment_id)
    now = datetime.now(timezone.utc).isoformat()
    
    if not os.path.exists(manifest_path):
        return IntegrityVerificationResult(
            assessment_id=assessment_id,
            overall_status="UNAVAILABLE",
            verified_at=now,
            artifacts_checked=0,
            unchanged_count=0,
            changed_count=0,
            missing_count=0,
            unavailable_count=0,
            artifact_results=[]
        )
        
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
        
    results = []
    unchanged = 0
    changed = 0
    missing = 0
    unavailable = 0
    
    for artifact in manifest_data.get("source_artifacts", []):
        source_name = artifact["source_name"]
        expected_hash = artifact["sha256"]
        
        filepath = current_files_map.get(source_name)
        
        if not filepath:
            status = "UNAVAILABLE"
            reason = "Filepath not provided for verification"
            current_hash = None
            unavailable += 1
        elif not os.path.exists(filepath):
            status = "MISSING"
            reason = "Source file is missing"
            current_hash = None
            missing += 1
        else:
            try:
                current_hash = get_file_sha256(filepath)
                if current_hash == expected_hash:
                    status = "UNCHANGED"
                    reason = "Hash matches exactly"
                    unchanged += 1
                else:
                    status = "CHANGED"
                    reason = "Hash mismatch - Evidence modified"
                    changed += 1
            except Exception as e:
                status = "UNAVAILABLE"
                reason = f"Error reading file: {str(e)}"
                current_hash = None
                unavailable += 1
                
        results.append(ArtifactVerificationResult(
            source_name=source_name,
            expected_hash=expected_hash,
            current_hash=current_hash,
            status=status,
            reason=reason
        ))
        
    if changed > 0:
        overall = "CHANGED"
    elif missing > 0:
        overall = "MISSING"
    elif unavailable > 0:
        overall = "UNAVAILABLE"
    else:
        overall = "UNCHANGED"
        
    return IntegrityVerificationResult(
        assessment_id=assessment_id,
        overall_status=overall,
        verified_at=now,
        artifacts_checked=len(results),
        unchanged_count=unchanged,
        changed_count=changed,
        missing_count=missing,
        unavailable_count=unavailable,
        artifact_results=results
    )
