
# 加密
def encrypt(plaintext, key):
    key_list = []
    ciphertext = ""
    for i in key:
        key_list.append(ord(i) - 65)    # 将密钥映射成数字数组

    for i in range(0, len(plaintext)):
        ciphertext += chr((ord(plaintext[i]) - 65 + key_list[i % len(key_list)]) % 26 + 65)     # 对明文每个字符和对应的密钥数字进行模26加

    return ciphertext

# 解密
def decrypt(ciphertext, key):
    key_list = []
    plaintext = ""
    for i in key:
        key_list.append(ord(i) - 65)

    for i in range(0, len(ciphertext)):
        plaintext += chr((ord(ciphertext[i]) - 65 - key_list[i % len(key_list)]) % 26 + 65)     # 对密文每个字符和对应的密钥数字进行模26减

    return plaintext


if __name__ == '__main__':
    operation = input("this is Vigenere, encrypt:1, decrypt:2, end:0: ")
    operations = ["0", "1", "2"]
    while operation not in operations:
        operation = input("error input, encrypt:1, decrypt:2, end:0: ")


    while operation != "0":
        if operation == "1":
            input_list = input("please input plaintext and key split by one space: ").split()
            plaintext = input_list[0]
            key = input_list[1]
            print("ciphertext: ", encrypt(plaintext, key))
        else:
            input_list = input("please input ciphertext and key split by one space: ").split()
            ciphertext = input_list[0]
            key = input_list[1]
            print("plaintext: ", decrypt(ciphertext, key))
        operation = input("do you want to continue? encrypt:1, decrypt:2, end:0: ")
        while operation not in operations:
            operation = input("error input, encrypt:1, decrypt:2, end:0: ")

    print("end")
    pass