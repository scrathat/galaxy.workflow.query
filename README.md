# Galaxy wokflow query
Search galaxy instances for workflows that are using a specific tool.

## Setup
To gather the workflows from the galaxy instances in `hosts.json` run
```
$ python workflows.py -t
```
It will also start a test server to serve the resulting `workflows.json` and its directory. 

Then run the client
```
$ cd client
$ yarn run serve
```