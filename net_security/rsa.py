import gmpy2


RSA_E = 40357           # 学号后五位为40359，不是质数，故选择相近的40357
RSA_P = gmpy2.mpz(pow(2, 127) + 45)
RSA_Q = gmpy2.mpz(pow(2, 127) + 65)

UP_ASCII_DIFF = 19      # 大写字符在ASCII和设定数字的差，以A为例，65 - 46 = 19
LOW_ASCII_DIFF = 77     # 小写字符在ASCII和设定数字的差，以a为例，97 - 20 = 77
NUM_ASCII_DIFF = 38     # 数字在ASCII和设定数字的差，以0为例，48 - 10 = 38


def find_prime():
    print(pow(2, 128) + 55)
    for i in range(0, 100):
        print(i, gmpy2.is_prime(gmpy2.mpz(pow(2, 127) + i)))


class RSA():
    def __init__(self, e, p, q):
        self.e = e
        self.p = p
        self.q = q

    def generate_key(self):     # 生成密钥，其中 l 为 p-1 和 q-1 的最小公倍数，d 为 e 的逆元
        n = self.p * self.q
        l = gmpy2.lcm(self.p - 1, self.q - 1)
        d = gmpy2.invert(self.e, l)
        return [self.e, n], [d, n]      # 返回公钥、私钥

    def change_text2num(self, text):    # 将明文变成整数数组
        res = []
        str_num = 0
        for i in range(0, len(text)):
            num = 0
            if 48 <= ord(text[i]) <= 57:
                num = ord(text[i]) - NUM_ASCII_DIFF
            elif 65 <= ord(text[i]) <= 90:
                num = ord(text[i]) - UP_ASCII_DIFF
            elif 97 <= ord(text[i]) <= 122:
                num = ord(text[i]) - LOW_ASCII_DIFF

            if (i % 2 != 0):            # 将单数位字符的变成四位整数的前两位，双数位变成后两位
                str_num += num
                res.append(str_num)
            else:
                str_num = num * 100
                if i == len(text) - 1:
                    res.append(str_num)
        return res

    def change_num2text(self, num_list):    # 将整数数组变回明文
        text = ""
        for i in num_list:
            a = [i // 100, i % 100]
            for j in a:
                if 10 <= j < 20:
                    text += chr(j + NUM_ASCII_DIFF)
                elif 20 <= j < 46:
                    text += chr(j + LOW_ASCII_DIFF)
                elif 46 <= j < 72:
                    text += chr(j + UP_ASCII_DIFF)
        return text



    def encrypt(self, plain_text, key):     # 加密
        plain_list = self.change_text2num(plain_text)

        cipher_list = []
        for i in plain_list:
            cipher_list.append(gmpy2.powmod(i, key[0], key[1]))
        return cipher_list

    def decrypt(self, cipher_list, key):    # 解密
        plain_list = []
        for i in cipher_list:
            plain_list.append(gmpy2.powmod(i, key[0], key[1]))
        return self.change_num2text(plain_list)
        
    

if __name__ == '__main__':
    rsa = RSA(RSA_E, RSA_P, RSA_Q)
    pk, sk = rsa.generate_key()

    print("公钥：", pk)
    print("私钥：", sk)

    plain_text = "IamVanDarkhole198"
    cipher_list = rsa.encrypt(plain_text, sk)
    
    print("加密结果：", cipher_list)
    print("解密结果：", rsa.decrypt(cipher_list, pk))
