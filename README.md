New York State Voters
=====================

This repository contains code to clean and load the New York State voter registration data, 
which can be requested from the [NYS Board of Elections](https://www.elections.ny.gov/FoilRequests.html).

The [Voter Registration Data File schema](https://www.elections.ny.gov/NYSBOE/Forms/FOIL_VOTER_LIST_LAYOUT.pdf)
is accessible as a PDF, and contains descriptions of the values for each field.

The data will be mailed as a zipped CSV file on a physical DVD.  You'll need to unzip the file, so you end up
with just a normal text file, e.g. `AllNYSVoters.txt`.

### Running

On your local workstation, clone this repository, then 

[Setup `gcloud`](#setup-gcloud) if you haven't yet.

Then install `bigquery` python library:

```
pip install -r requirements.txt
```

Now run the upload:

```
./csv2json.py AllNYSVoters.txt nysvoters.json | ./bqstream.py -d [your dataset] -t [your table] nysvoters.json
```

*csv2json.py*

Cleans and converts the CSV to a JSON format, writing to `STDOUT`.

*bqstream.py*

Takes line-delimited JSON from `STDIN`, and batch streams it to the specified table.


### Setup Gcloud

[Download and Install gcloud SDK](https://cloud.google.com/sdk/downloads)

```
gcloud init # choose your project, zone, etc.

# Create credentials
gcloud auth login
gcloud auth application-credentials login
```
