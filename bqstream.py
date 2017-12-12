#!/usr/bin/env python

import json
import argparse
import pprint
import sys
from collections import OrderedDict
from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField

bigquery_client = bigquery.Client()


def flush(buffer, table, count):
    errors = bigquery_client.create_rows(table, buffer)
    if errors:
        print('Errors:')
        pprint.pprint(errors)

    return len(buffer)


def parse(schema):
    return [SchemaField(field_type=i.get('type').upper(),
                        fields=parse(i.get('fields', ())),
                        mode=i.get('mode', 'NULLABLE').upper(),
                        name=i.get('name'),
                        description=i.get('description', ''))
            for i in schema]


def main(dataset_id, table_id, batchsize, schema):

    schemafields = parse(json.load(schema))

    print 'Parsed schema:'
    pprint.pprint(schemafields)

    dsref = bigquery_client.dataset(dataset_id)
    try:
        bigquery_client.create_dataset(bigquery.Dataset(dsref))
    except Exception:
        pass

    table = bigquery.Table(dsref.table(table_id))
    table.schema = schemafields
    try:
        bigquery_client.create_table(table)
    except Exception:
        pass

    buffer = []
    count = 0

    print 'Reading from STDIN...'
    for line in sys.stdin:
        try:
            obj = json.loads(line, object_pairs_hook=OrderedDict)
            buffer.append(tuple([v for k, v in obj.items()]))
            if len(buffer) >= batchsize:
                count = count + flush(buffer, table, count)
                print('Loaded {} rows'.format(count))
                buffer = []
        except Exception as e:
            print e
            print "-------START ERROR-------"
            print "Could not process:", line
            print "--------END ERROR--------"

    if len(buffer) > 0:
        count = count + flush(buffer, table, count)
        print('Finished. Loaded {} rows'.format(count))
        buffer = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stream STDIN lines as rows for the given schema into BigQuery')
    parser.add_argument('-d', '--dataset', help='Dataset to load')
    parser.add_argument('-t', '--table', help='Table to load')
    parser.add_argument('-b', '--batchsize', type=int, help='batchsize', default=500)
    parser.add_argument('schemafile', help='A JSON-format BiqQuery schema file')
    args = parser.parse_args()

    main(args.dataset, args.table, args.batchsize, open(args.schemafile, 'r'))
