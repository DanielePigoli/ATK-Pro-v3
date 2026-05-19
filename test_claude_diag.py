import os
import sys
import logging

# Aggiungi src al path per caricare KeyManager
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from key_manager import KeyManager
    km = KeyManager()
    keys = km.get_all_keys("Claude")
    
    if not keys:
        print("ERRORE: Nessuna chiave Claude trovata nel Caveau!")
        sys.exit(1)
        
    key = keys[0].strip()
    print(f"Testando la prima chiave Claude (inizia con: {key[:10]}...)")
    
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    
    print("\n--- TEST 1: Lista modelli (se supportata) ---")
    try:
        # Nota: l'SDK Anthropic non ha un metodo list() pubblico standard come OpenAI, 
        # ma proviamo a fare una chiamata minima.
        pass
    except Exception as e:
        print(f"Salto lista modelli: {e}")

    print("\n--- TEST 2: Chiamata minima con Haiku ---")
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Ciao"}]
        )
        print(f"SUCCESSO! Risposta: {message.content[0].text}")
    except Exception as e:
        print(f"FALLIMENTO con Haiku: {e}")

    print("\n--- TEST 3: Chiamata minima con Sonnet 3.5 (Old) ---")
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=10,
            messages=[{"role": "user", "content": "Ciao"}]
        )
        print(f"SUCCESSO! Risposta: {message.content[0].text}")
    except Exception as e:
        print(f"FALLIMENTO con Sonnet 3.5 (v1): {e}")

except Exception as e:
    print(f"ERRORE GENERALE: {e}")
