from flask import Flask, Response, request
import gzip
import io
import requests
import os
import logger
import cherrypy
import ujson

app = Flask(__name__)
logger = logger.Logger('file-source-downloader-service')
headers = ujson.loads('{"Content-Type": "application/json"}')

download_url = os.environ.get("download_url")
exposed_filename = os.environ.get("exposed_filename")
is_zip_file = os.environ.get("is_zip_file", "false") == "true"
tmp_filename = f"tmp_{exposed_filename}.json"


class DataAccess:

    def __get_all_entities(self):
        json_file = open(tmp_filename, 'rb')
        json_content = json_file.read()
        entities = ujson.loads(json_content.decode('utf-8'))

        if isinstance(entities, dict):
            entities = [entities]

        for entity in entities:
            if entity is not None:
                yield (entity)

    def get_all_entities(self):
        return self.__get_all_entities()


data_access_layer = DataAccess()


def download_file():
    with requests.get(download_url, headers=headers) as r:
        if is_zip_file:
            compressed_file = io.BytesIO(r.content)
            decompressed_file = gzip.decompress(compressed_file.read())

            open(tmp_filename, 'wb').write(decompressed_file)
        else:
            open(tmp_filename, 'wb').write(r.content)

        logger.info(f"File downloaded from url: {download_url}")


def stream_json(data):
    first = True
    yield '['
    for i, row in enumerate(data):
        if not first:
            yield ','
        else:
            first = False
        yield ujson.dumps(row)
    yield ']'


@app.route("/", methods=["GET"])
def get():
    logger.info(f"Fetching data from '{tmp_filename}'")
    if request.args.get("force_refresh") is not None:
        force_refresh = request.args["force_refresh"]
        if force_refresh == "true":
            download_file()

    entities = data_access_layer.get_all_entities()

    return Response(stream_json(entities), mimetype='application/json')


if __name__ == '__main__':
    download_file()

    cherrypy.tree.graft(app, '/')

    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        'environment': 'production',
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': 5002,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()
