import math
import os,sys

colored_string = lambda color_code,msg:f"{color_code}{msg}\33[0;30m"


class HuffmenEncodeing:
    def __init__(self, file_path, output=None):
        self.file_path = file_path
        self.output_path = ""
        self.codecs = {}
        self.reversed_codecs = {}
        self.encoding_byte_size = 2

        if output:
            self.output_path = output
        else:
            path, file = os.path.split(self.file_path)
            self.output_path = os.path.join(path,f"{file.split('.')[0]}.bin")

    class HuffmenTreeNode:
        def __init__(self, super_self, ch=None,value=None):
            if isinstance(super_self,HuffmenEncodeing):
                self.super_self = super_self
            else:
                raise TypeError(f"super_self required object of type HuffmenEncoding not {type(super_self)}")

            self.ch=ch
            self.value = value
            self.code = {}
            self.left = None
            self.right = None

        def generate_codecs(self, code=None):
            if code and self.ch:
                self.super_self.codecs[self.ch] = code
                self.super_self.reversed_codecs[code] = self.ch
                return
            if self.left:
                self.left.generate_codecs(code+"0" if code else "0")
            if self.right:
                self.right.generate_codecs(code+"1" if code else "1")

        def __add__(self, other):
            if isinstance(other,self.__class__):
                return self.__class__(self.super_self,value=self.value+other.value)

        __gt__ = lambda self,other: True if self.value>other.value else False
        __lt__ = lambda self,other: True if self.value<other.value else False
        __str__ = lambda self: f"<{self.ch}: {self.value}>" if self.ch else self
        __repr__ = lambda self: f"<{self.ch}: {self.value}>" if self.ch else self

    def get_char_list(self, st):
        chars = list(st)
        char_list = []
        while chars:
            ch = chars.pop()
            if ch not in char_list:
                char_list.append(ch)
        return char_list

    def get_frequency_dict(self, st):
        char_li =self.get_char_list(st)
        dic = {}
        for ch in char_li:
            dic[ch] = st.count(ch)
        return dic

    def get_priority_que(self, string):
        dic = self.get_frequency_dict(string)
        leafs = []
        for key, value in dic.items():
            leafs.append(self.HuffmenTreeNode(self,key,value))
        leafs.sort(reverse=True)
        return leafs

    def build_huffmen_tree(self, p_list):
        cur_node = None
        while len(p_list)>1:
            node_1 = p_list.pop()
            node_2 = p_list.pop()
            cur_node = node_1+node_2
            cur_node.left,cur_node.right = node_1, node_2
            p_list.append(cur_node)
            p_list.sort(reverse=True)
        return cur_node

    def generate_codes_and_save(self, tree):
        tree.generate_codecs()

    def get_encoded_string(self, text):

        bit_string = ""
        for ch in text:
            bit_string+=self.codecs[ch]
        return  bit_string

    def convert_to_bit_string(self, byte_string):
        if type(byte_string) != bytes:
            raise TypeError(f"Expected encoded bytes object not {type(byte_string)}")
        bit_st = ""
        for ch in byte_string:
            byte=bin(ch)[2:].rjust(8,'0')
            bit_st+=byte
        return bit_st

    def convert_to_string(self, byte_string):
        byte_values = []
        cur_bits = ""
        index = 0
        for ch in byte_string:
            cur_bits+=ch
            if len(cur_bits) == 8:
                # if int(cur_bits,base=2)>=128:
                #     print(int(cur_bits,base=2))
                byte_values.append(int(cur_bits,base=2))
                cur_bits = ""
        return bytes(byte_values).decode()

    def get_reversed_codecs_in_bit_st(self):
        values = ""
        chars = ""
        max_code_len = 0
        for i in self.reversed_codecs.keys():
            max_code_len = len(i) if len(i)>max_code_len  else max_code_len

        bits_needed_to_store_code_len = math.ceil(math.log2(max_code_len+1))
        for value,key in self.reversed_codecs.items():
            values+=bin(len(value))[2:].rjust(bits_needed_to_store_code_len,'0')+value
            chars+=key

        encoded_chars = chars.encode()
        encoded_chars_len = len(encoded_chars)
        chars_in_bit_st = self.convert_to_bit_string(encoded_chars)

        bits_for_encoded_chars_len = math.ceil(math.log2(encoded_chars_len))

        codecs = bin(bits_for_encoded_chars_len)[2:].rjust(4,'0')\
                +bin(bits_needed_to_store_code_len)[2:].rjust(4,'0')\
                +bin(encoded_chars_len)[2:].rjust(bits_for_encoded_chars_len)\
                +chars_in_bit_st+values
        return codecs

    def add_reversed_codecs(self, bit_st):
        r_codecs_bit_string = self.get_reversed_codecs_in_bit_st()
        codec_len = len(r_codecs_bit_string)
        codec_info_len = math.ceil(math.log2(codec_len+1))
        modified_bit_st = bin(codec_info_len)[2:].rjust(4,'0')\
                            +bin(codec_len)[2:].rjust(codec_info_len,'0')\
                            +bit_st+r_codecs_bit_string
        return modified_bit_st

    def getbitstream(self, bit_st):
        bit_stream = bytearray(math.ceil(len(bit_st)/8))
        byte_st = ""
        index=0
        for bit in bit_st:
            byte_st+=bit
            if len(byte_st) == 8:
                bit_stream[index]=int(byte_st,base=2)
                index+=1
                byte_st=""
        if byte_st:
            bit_stream[index]=int(byte_st,base=2)
        return bit_stream

    def add_padding(self, bit_string):
        pad_info_length = 4
        length = pad_info_length+len(bit_string)
        pading_length =  8-length%8
        return bin(pading_length)[2:].rjust(4,'0')+bit_string+"0"*pading_length

    def remove_padding(self, bit_string):
        padding_info, string = bit_string[:4], bit_string[4:]
        padding_length = int(padding_info,base=2)

        return string[:-padding_length]

    def extract_codec_info_and_save(self, bit_string):
        # extract the codecs and save it to self
        pre_codec_info, bit_string = int(bit_string[:4],base=2), bit_string[4:]
        codec_info, bit_string = int(bit_string[:pre_codec_info],base=2), bit_string[pre_codec_info:]
        bit_codecs, bit_string = bit_string[-codec_info:], bit_string[:-codec_info]

        bits_for_char_len, codecs= int(bit_codecs[:4],base=2),bit_codecs[4:]
        bits_needed_to_store_code_len,codecs = int(codecs[:4],base=2),codecs[4:]
        encoded_chars_len, codecs = int(codecs[:bits_for_char_len],base=2),codecs[bits_for_char_len:]
        chars_in_bit_st, values = codecs[:encoded_chars_len*8],codecs[encoded_chars_len*8:]
        chars = self.convert_to_string(chars_in_bit_st)
        value_list = []
        while values:
            next_code_len,values = int(values[:bits_needed_to_store_code_len],base=2),\
                              values[bits_needed_to_store_code_len:]
            next_code_value,values = values[:next_code_len],\
                                     values[next_code_len:]
            value_list.append(next_code_value)
        for code,char in zip(value_list,chars):
            self.reversed_codecs[code] = char
        return bit_string

    def decode_bit_string(self, bit_string):

        cur_bits = ""
        cur_string = ""
        for bit in bit_string:
            cur_bits+=bit
            if cur_bits in self.reversed_codecs:
                cur_string+= self.reversed_codecs[cur_bits]
                cur_bits=""
        return cur_string

    def compress(self):
        # read the text from the file
        with open(self.file_path,'r',encoding='utf') as input_file, open(self.output_path, 'wb') as output_file:
            text = ''.join(input_file.readlines())
            p_list = self.get_priority_que(text)

            tree = self.build_huffmen_tree(p_list)
            self.generate_codes_and_save(tree)
            bit_st = self.get_encoded_string(text)
            bit_st = self.add_reversed_codecs(bit_st)
            padded_bit_st = self.add_padding(bit_st)
            bit_stream = self.getbitstream(padded_bit_st)
            output_file.write(bit_stream)
        if os.stat(self.file_path).st_size<os.stat(self.output_path).st_size:
            msg = """
                It is not wise to compress a reletively small file. 
            """
            print(colored_string('\33[;31m',msg),end='')
            msg = """
                The result could be a nightmare when you'll see 
                the compressed file is larger than it's original size.
            """
            print(colored_string('\33[1;31m',msg))

    def decompress(self):
        path, file = os.path.split(self.file_path)
        output_path = os.path.join(path,f"{file.split('.')[0]}.txt")
        with open(self.file_path,'rb') as input_file, open(output_path, 'w',encoding='utf-8') as output_file:
            byte = input_file.read(1)
            bit_string = ""
            while len(byte)>0:

                bit_string+=bin(ord(byte))[2:].rjust(8,'0')
                byte = input_file.read(1)
            bit_string = self.remove_padding(bit_string)
            bit_string = self.extract_codec_info_and_save(bit_string)
            text_string = self.decode_bit_string(bit_string)
            output_file.write(text_string)

