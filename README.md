Galaxy wokflow query
====================

Search galaxy instances for workflows that are using a specific tool.

Setup
-----

To gather the workflows from the galaxy instances in `hosts.json` and serve them on `localhost:8082` run

```shell
cd backend
python workflows.py -t
```

Then run the client

```shell
cd client
yarn run serve
```
