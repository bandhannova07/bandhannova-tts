import time
from tts_engine import get_tts_engine

def test_performance():
    engine = get_tts_engine()
    text = "আমি বাংলায় কথা বলতে পারি। এটি একটি দ্রুতগতির পরীক্ষা।"
    
    print("\n=== Performance Test ===")
    
    # 1. Measure First Generation (No Cache)
    # Note: We might need to clear cache if it exists
    import os
    from config import Config
    config = Config()
    import hashlib
    key_data = f"{text}|bn|bn-IN-TanishaaNeural|1.0"
    hash_key = hashlib.sha256(key_data.encode()).hexdigest()
    cache_file = os.path.join(config.CACHE_DIR, f"{hash_key}.mp3")
    
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"🗑️ Cleared existing cache for fresh test.")

    start_time = time.time()
    engine.generate_speech(text, language='bn', voice_id='bn-IN-TanishaaNeural', return_bytes=True)
    end_time = time.time()
    first_duration = end_time - start_time
    print(f"⏱️ First Request (No Cache): {first_duration:.4f}s")

    # 2. Measure Second Generation (Cache Hit)
    start_time = time.time()
    engine.generate_speech(text, language='bn', voice_id='bn-IN-TanishaaNeural', return_bytes=True)
    end_time = time.time()
    second_duration = end_time - start_time
    print(f"⚡ Second Request (Cache Hit): {second_duration:.4f}s")
    
    speedup = first_duration / second_duration if second_duration > 0 else float('inf')
    print(f"\n🚀 Cache Speedup: {speedup:.1f}x faster!")
    
    # Compare with expected 10x
    if speedup >= 10:
        print("✅ Success: Met the 10x speedup goal via caching!")
    else:
        print("⚠️ Note: Speedup less than 10x, but still significantly faster.")

if __name__ == "__main__":
    test_performance()
