from app import create_app

app = create_app("/var/mythapi/data")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=8, dev=True)