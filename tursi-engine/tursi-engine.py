import argparse
print("Welcome to tursi-engine!")
parser = argparse.ArgumentParser(description="tursi-engine: Deploy AI models.")
parser.add_argument("up", nargs="?", help="Deploy a model")
args = parser.parse_args()
if args.up:
    print("Deploying model... (coming soon!)")