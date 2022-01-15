import pickle
import sys,math
import huffmentree as hft


def main(*args,**kwargs):
    cmd, path = args[0][1],args[0][2]
    if cmd == "zip":
        obj = hft.HuffmenEncodeing(path)
        obj.compress()
    elif cmd == "unzip":
        obj = hft.HuffmenEncodeing(path)
        obj.decompress()

if __name__ == "__main__":
    main(sys.argv)
