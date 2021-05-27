## File source downloader service

A service that can be used to download a file from an external source, store it locally and use it as a source in Sesam. 

[![SesamCommunity CI&CD](https://github.com/sesam-community/file-source-downloader-service/actions/workflows/sesam-community-ci-cd.yml/badge.svg)](https://github.com/sesam-community/file-source-downloader-service/actions/workflows/sesam-community-ci-cd.yml)

### Environment variables:

`download_url` - the url to the external file.

`exposed_filename` - name of the file to store the contents of the downloaded file in.

`is_zip_file` - set this to true if the external file is a zip file, the service will then unzip the contents before storing it in the local file.

### Querystring parameters:

`force_refresh_` - if set to true will download the external file upon request.


### Example system config:

```json
{
  "_id": "file-source-download-system",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "download_url": "https://url/filename",
      "exposed_filename": "filename"
    },
    "image": "sesamcommunity/file-source-downloader-service:latest",
    "port": 5001
  }
}

```

### Example pipe using the microservice above

```json
{
  "_id": "file-source-download-pipe",
  "type": "pipe",
  "source": {
    "is_chronological": false,
    "is_since_comparable": false,
    "supports_since": false,
    "system": "file-source-download-system",
    "type": "json",
    "url": ""
  }
}

```