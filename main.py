import sys
from PIL import Image

# Formats supportes
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'gif']

def encode_message(input_image_path, output_image_path, secret_message):
    """Encode un message secret dans une image."""
    img = Image.open(input_image_path)
    img = img.convert("RGB")

    # Convertir le message en binaire
    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
    binary_message += '1111111111111110'  # Delimiteur
    print("Message binaire a encoder :", binary_message[:64], "...")  # Affiche les premiers bits

    # Verification de la capacite de l'image
    img_data = list(img.getdata())
    if len(binary_message) > len(img_data) * 3:
        raise ValueError("Le message est trop long pour cette image.")

    # Encodage des bits dans les LSB des pixels
    data_index = 0
    new_data = []
    for pixel in img_data:
        new_pixel = list(pixel) # Creer une copie du tuple pixel
        for i in range(3):  # R, G, B
            if data_index < len(binary_message):
                new_pixel[i] = (new_pixel[i] & ~1) | int(binary_message[data_index])
                data_index += 1
        new_data.append(tuple(new_pixel))

    # Sauvegarde de l'image encodee
    img.putdata(new_data)
    img.save(output_image_path)
    print(f"\033[32mMessage cache avec succes dans :  {output_image_path}\033[0m")  # Texte en vert

def decode_message(image_path):
    """Decode un message cache dans une image."""
    img = Image.open(image_path)
    img_data = list(img.getdata())
    binary_message = ""
    decoded_message = ""

    print("Decodage des bits...")
    for pixel in img_data:
        for i in range(3):
            binary_message += str(pixel[i] & 1)

    print(f"Bits extraits (premiers 64 bits) : {binary_message[:64]}")

    # Reconstruction du message avec arret sur le delimiteur
    byte_string = ""
    for bit in binary_message:
        byte_string += bit
        if len(byte_string) == 8:  # Un octet complet
            if byte_string == '11111111': #check for delimiter
                break #exit loop if delimiter is found
            try:
                decoded_message += chr(int(byte_string, 2))
            except ValueError:
                print(f"Erreur de conversion binaire vers caractere a l'octet : {byte_string}")
                return "" # Return empty string on error
            byte_string = ""  # Reinitialiser pour le prochain octet

    print(f"\033[31mMessage decode : {decoded_message}\033[0m")  # Texte en rouge
    return decoded_message

def compare_images(image1_path, image2_path):
    """Compare deux images et affiche le nombre de pixels modifies."""
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)

    if img1.size != img2.size:
        print("Les images ont des tailles differentes.")
        return

    differences = 0
    for pixel1, pixel2 in zip(img1.getdata(), img2.getdata()):
        if pixel1 != pixel2:
            differences += 1

    print(f"Nombre de pixels modifies : {differences}")

if __name__ == "__main__":
    # Gestion des commandes de ligne
    if len(sys.argv) < 2:
        print("Usage : python main.py <command> [arguments]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "hide":
        if len(sys.argv) != 5:
            print("Usage : python main.py hide <input_image> <output_image> <message>")
            sys.exit(1)
        input_image = sys.argv[2]
        output_image = sys.argv[3]
        message = sys.argv[4]
        encode_message(input_image, output_image, message)

    elif command == "reveal":
        if len(sys.argv) != 3:
            print("Usage : python main.py reveal <encoded_image>")
            sys.exit(1)
        encoded_image = sys.argv[2]
        decode_message(encoded_image)

    elif command == "compare":
        if len(sys.argv) != 4:
            print("Usage : python main.py compare <original_image> <modified_image>")
            sys.exit(1)
        original_image = sys.argv[2]
        modified_image = sys.argv[3]
        compare_images(original_image, modified_image)

    else:
        print("Commandes disponibles : hide, reveal, compare")
        sys.exit(1)
