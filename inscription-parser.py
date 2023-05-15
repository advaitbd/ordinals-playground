import sys, os, base64, argparse
import requests

# def get_cli_args():
# 	ap = argparse.ArgumentParser(description="Parse and output the ordinal inscription inside transaction")
# 	if sys.stdin.isatty():
# 		ap.add_argument("tx_file", help="input raw transaction file")

# 	ap.add_argument("-du", "--data-uri", action="store_true", help="print inscription as data-uri instead of writing to a file")
# 	ap.add_argument("-o", "--output", help="write inscription to OUTPUT file")

# 	return ap.parse_args()

def get_cli_args():
    ap = argparse.ArgumentParser(description="Parse and output the ordinal inscription inside transaction")
    ap.add_argument("-du", "--data-uri", action="store_true", help="print inscription as data-uri instead of writing to a file")
    ap.add_argument("-o", "--output", help="write inscription to OUTPUT file")
    ap.add_argument("tx_id", help="transaction ID to retrieve from the API")
    return ap.parse_args()

def get_raw_data(tx_id):
    url = f"https://mempool.space/api/tx/{tx_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve transaction data for {tx_id} from the API", file=sys.stderr)
        sys.exit(1)
	
	# extract the txid.vin.witness field from the response
    tx_witness = response.json()["vin"][0]["witness"]
    # concatenate tx_witness array into a single string
    tx_witness = "".join(tx_witness)
    
    return bytes.fromhex(tx_witness)

# def read_raw_data():
# 	if not sys.stdin.isatty():
# 		raw = bytes.fromhex(sys.stdin.read())
# 	else:
# 		file = open(args.tx_file)
# 		raw = bytes.fromhex(file.read())
# 		file.close()
  
# 	return raw

def read_bytes(n = 1):
	global pointer

	value = raw[pointer : pointer + n]
	pointer += n
	return value

def get_initial_position():
	inscription_mark = bytes.fromhex("0063036f7264")
	try:
		return raw.index(inscription_mark) + len(inscription_mark)
	except ValueError:
		print(f"No ordinal inscription found in transaction", file = sys.stderr)
		sys.exit(1)

def read_content_type():
	OP_1 = b"\x51"
  
	byte = read_bytes()
	if byte != OP_1:
		assert(byte == b'\x01')
		assert(read_bytes() == b'\x01')

	size = int.from_bytes(read_bytes(), "big")
	content_type = read_bytes(size)
	return content_type.decode("utf8")

def read_pushdata(opcode):
	int_opcode = int.from_bytes(opcode, "big")

	if 0x01 <= int_opcode <= 0x4b:
		return read_bytes(int_opcode)
	
	num_bytes = 0
	match int_opcode:
		case 0x4c:
			num_bytes = 1
		case 0x4d:
			num_bytes = 2
		case 0x4c:
			num_bytes = 4
		case _:
			print(f"Invalid push opcode {hex(int_opcode)} at position {pointer}", file = sys.stderr)
			sys.exit(1)
	
	size = int.from_bytes(read_bytes(num_bytes), "little")
	return read_bytes(size)

def write_data_uri(data, content_type):
	data_base64 = base64.encodebytes(data).decode("ascii").replace("\n", "")
	print(f"data:{content_type};base64,{data_base64}")

def write_file(data,ext):
	filename = args.output
	if filename is None:
		filename = base_filename = f"out"
	else:
		base_filename = filename
		
	i = 1	
	while os.path.isfile(filename):
		i += 1
		filename = f"{base_filename}{i}"

	print(f"Writing contents to file \"{filename}\"")
	f = open(filename + f".{ext}", "wb")
	f.write(data)
	f.close()

def get_file_extension(content_type):
    switcher = {
        "text/plain;charset=utf-8": "txt",
        "text/html;charset=utf-8": "html"
    }
    file_extension = switcher.get(content_type, content_type.split("/")[1])
    return file_extension


def main():
	global args, raw, pointer
	
	args = get_cli_args()
	raw = get_raw_data(args.tx_id)
	pointer = get_initial_position()

	content_type = read_content_type()
	print(f"Content type: {content_type}")

	file_extension = get_file_extension(content_type)

	assert(read_bytes() == b'\x00')

	data = bytearray()

	OP_ENDIF = b"\x68"
	opcode = read_bytes()
	while opcode != OP_ENDIF:
		chunk = read_pushdata(opcode)
		data.extend(chunk)
		opcode = read_bytes()

	print(f"Total size: {len(data)} bytes")
	if args.data_uri:
		write_data_uri(data, content_type)
	else:
		write_file(data,file_extension)
	
	print("\nDone")

main()