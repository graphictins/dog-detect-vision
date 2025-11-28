import requests
import threading

WEBHOOK_URLS = (
    "https://discordapp.com/api/webhooks/1393927939376156702/jMnEbAosI8MG4srmfxHUuyFrZMkSpeameUyUOdO_br4X3Q-IWViro8mC4pDEiscYC91e",
)

def _core_send_message(text="content missing", files_dict=None, verbose=False): 
    message = {
        "username": "DOGGO Detection",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "content": text
    }

    url_count = 0

    for url in WEBHOOK_URLS:
        url_count += 1
        
        # --- THE FIX IS HERE ---
        # If we have a file, we must rewind it to the beginning (0) 
        # for every new request, or the second webhook gets 0 bytes.
        if files_dict:
            for key, (filename, file_obj) in files_dict.items():
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)

        try:
            response = requests.post(url, data=message, files=files_dict)

            if response.status_code in (204, 200):
                if verbose: 
                    print(f"URL {url_count} ✅ Discord Message sent successfully!")
            else:
                if verbose: 
                    print(f"URL {url_count} ❌ Failed to send. Status: {response.status_code}")
                    print(response.text)
        except Exception as e:
            print(f"URL {url_count} ❌ Network Error: {e}")


def send_message(text, file_path=None, verbose=False):
    """
    Wrapper to handle file opening safely before threading.
    """
    if file_path:
        # We start the thread using a helper that opens the file inside the thread
        # to ensure it stays open during the network request.
        thread = threading.Thread(target=_threaded_file_sender, args=(text, file_path, verbose))
        thread.daemon = True
        thread.start()
    else:
        # Text only
        thread = threading.Thread(target=_core_send_message, args=(text, None, verbose))
        thread.daemon = True
        thread.start()


def _threaded_file_sender(text, file_path, verbose):
    """
    Opens the file, sends it, and ensures it closes automatically.
    """
    try:
        with open(file_path, 'rb') as f:
            # We pass the open file object to the core sender
            files = {'file': (file_path, f)}
            _core_send_message(text, files, verbose)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}")
    except Exception as e:
        print(f"❌ Error opening file: {e}")

if __name__ == "__main__":
    # Test Text
    send_message("This text is a test")
    
    # Test File (Create a dummy file first if you want to test this)
    # with open("test.txt", "w") as f: f.write("test")
    # send_message("This is a file test", "test.txt", True)