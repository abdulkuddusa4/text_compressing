import sys,logging
import huffmentree as hft

colored_string = lambda color_code,msg:f"{color_code}{msg}\33[30m"


def main(cmd,path):
    if cmd == "-zip":
        obj = hft.HuffmenEncodeing(path)
        obj.compress()
    elif cmd == "-uzip":
        obj = hft.HuffmenEncodeing(path)
        obj.decompress()
    else:
        msg = """
            invalid command.
            command: zip(for compressing)/-uzip(for decompressing)
        """
        print(colored_string('\33[31m',msg))

if __name__ == "__main__":
    try:
        cmd, file_path = sys.argv[1],sys.argv[2]
        main(cmd, file_path)
    except IndexError as e:
        if not len(e.args)>1:
            msg = """
                you should specify a command and the file path
                in the following format:
                *** python main.py -zip/-uzip filepath *** \n
                for example: python main.py zip your_file_path\n
            """
            print(colored_string('\33[31m',msg))
            exit()
    except FileNotFoundError as e:
        print(colored_string('\33[31',"file path: {e.filename} \ndoes not exists"))
    except UnicodeDecodeError as e:
        if cmd == 'compress':
            msg = """
                you are probably trying to compress a non-text file.
                if that is the case. please try with a text file.
                this application does not support compression for image or autdio/video file.

                the other reason could be that you are trying to compress an already
                compressed file.
            """
        else:
            msg = """
                you are probably trying to decompress a file that is not
                compressed using this application
            """
        print(colored_string('\33[31m',msg))


