import requests

def get_witness_data(tx_id):
    url = f"https://mempool.space/api/tx/{tx_id}"

    
    response = requests.get(url)

    # extract the txid.vin.witness field from the response
    tx_witness = response.json()["vin"][0]["witness"]
    # concatenate tx_witness array into a single string
    tx_witness = "".join(tx_witness)
    print(tx_witness)
    return tx_witness


get_witness_data("859eecab0a9665bf1117664d774ef5490b06232fcc024bf2e08f712cbb8ad059")