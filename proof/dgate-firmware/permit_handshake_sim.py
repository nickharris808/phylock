import sqlite3
import os
import threading
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hashes
import matplotlib.pyplot as plt
import numpy as np

"""
D-Gate+: Permit Handshake & Atomic Quota Simulator
Part of the Sovereign Handshake Protocol (SHP) Week 2 Technical Brief.

This script simulates:
1. Ed25519 Signed Permit Validation.
2. Atomic Quota Management using SQLite WAL mode.
3. High-concurrency stress test to prove 0 double-spend events.
"""

DB_PATH = "permits.db"
NUM_THREADS = 200
QUOTA_LIMIT = 50

class PermitManager:
    def __init__(self):
        self.init_db()
        # Generate signing key for the "Operator"
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
    def init_db(self):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("CREATE TABLE permits (id TEXT PRIMARY KEY, remaining_uses INTEGER);")
        conn.execute("INSERT INTO permits (id, remaining_uses) VALUES ('PERMIT_001', ?);", (QUOTA_LIMIT,))
        conn.commit()
        conn.close()

    def sign_permit(self, permit_id):
        return self.private_key.sign(permit_id.encode())

    def verify_and_use_permit(self, permit_id, signature):
        # 1. Cryptographic Verification
        try:
            self.public_key.verify(signature, permit_id.encode())
        except Exception:
            return False, "CRYPTO_FAILURE"

        # 2. Atomic Database Update
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            cursor = conn.execute(
                "UPDATE permits SET remaining_uses = remaining_uses - 1 "
                "WHERE id = ? AND remaining_uses > 0 RETURNING remaining_uses;",
                (permit_id,)
            )
            row = cursor.fetchone()
            conn.commit()
            if row:
                return True, f"SUCCESS (Rem: {row[0]})"
            else:
                return False, "QUOTA_EXHAUSTED"
        except sqlite3.OperationalError as e:
            return False, f"DB_BUSY: {e}"
        finally:
            conn.close()

def stress_test():
    pm = PermitManager()
    permit_id = "PERMIT_001"
    signature = pm.sign_permit(permit_id)
    
    results = {"SUCCESS": 0, "QUOTA_EXHAUSTED": 0, "OTHER": 0}
    lock = threading.Lock()

    def worker():
        success, msg = pm.verify_and_use_permit(permit_id, signature)
        with lock:
            if success:
                results["SUCCESS"] += 1
            elif msg == "QUOTA_EXHAUSTED":
                results["QUOTA_EXHAUSTED"] += 1
            else:
                results["OTHER"] += 1

    threads = []
    print(f"Launching {NUM_THREADS} concurrent attachment threads for {QUOTA_LIMIT} permit slots...")
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Test Results: {results}")
    
    # Validation
    if results["SUCCESS"] == QUOTA_LIMIT:
        print("STATUS: ✅ ATOMICITY PROVEN (No Double-Spend)")
    else:
        print(f"STATUS: ❌ ATOMICITY FAILED (Expected {QUOTA_LIMIT}, got {results['SUCCESS']})")

    # Generate Chart
    labels = ['Successful Attachments', 'Rejected (Exhausted)', 'Errors']
    values = [results["SUCCESS"], results["QUOTA_EXHAUSTED"], results["OTHER"]]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=['#00FF41', '#FF4136', '#AAAAAA'])
    plt.axhline(y=QUOTA_LIMIT, color='black', linestyle='--', label=f'Quota Limit ({QUOTA_LIMIT})')
    plt.title('D-Gate+ Atomic Quota Stress Test (200 Threads)')
    plt.ylabel('Count')
    plt.grid(axis='y', alpha=0.3)
    
    # Add labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, int(yval), ha='center', fontweight='bold')

    plt.legend()
    plt.savefig('atomic_quota_results.png')
    print("Saved atomic_quota_results.png")

if __name__ == "__main__":
    stress_test()

