from ord import client

for i, inscription_id in client.inscriptions(0,100):
    inscription = client.get_content(inscription_id)
    try:
        plaintext = inscription.decode("utf-8")
        print(i, inscription_id, "plaintext content")
        print(plaintext, "\n\n")
    except UnicodeDecodeError:
        pass