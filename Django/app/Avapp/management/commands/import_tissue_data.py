# # Avapp/management/commands/import_tissue_data.py
#
# from django.core.management.base import BaseCommand, CommandError
# import csv
# from Avapp.models import TissueCorrelation
#
# class Command(BaseCommand):
#     help = 'Import tissue CSV data with corresponding pvalues, stopping after 1,000,000 records.'
#
#     def add_arguments(self, parser):
#         parser.add_argument(
#             'csv_path',
#             type=str,
#             help='Path to the main CSV file (e.g., ileum_to_ileum.csv)'
#         )
#         parser.add_argument(
#             'pvalue_csv_path',
#             type=str,
#             help='Path to the pvalue CSV file (e.g., ileum_to_ileum_pvalue.csv)'
#         )
#         parser.add_argument(
#             '--from_tissue',
#             type=str,
#             required=True,
#             help='Name of the source tissue'
#         )
#         parser.add_argument(
#             '--to_tissue',
#             type=str,
#             required=True,
#             help='Name of the destination tissue'
#         )
#         parser.add_argument(
#             '--delimiter',
#             type=str,
#             default=',',
#             help='CSV delimiter (default is ",")'
#         )
#
#     def handle(self, *args, **options):
#         csv_path = options['csv_path']
#         pvalue_csv_path = options['pvalue_csv_path']
#         from_tissue = options['from_tissue']
#         to_tissue = options['to_tissue']
#         delimiter = options['delimiter']
#
#         self.stdout.write(f"Importing main data from: {csv_path}")
#         self.stdout.write(f"Importing pvalues from: {pvalue_csv_path}")
#         self.stdout.write(f"Tissue relation: {from_tissue} -> {to_tissue}")
#
#         max_inserts = 101000000  # Stop after 100M records
#         inserted_count = 0
#
#         try:
#             with open(csv_path, newline='', encoding='utf-8') as main_file, \
#                  open(pvalue_csv_path, newline='', encoding='utf-8') as pvalue_file:
#
#                 main_reader = csv.DictReader(main_file, delimiter=delimiter)
#                 pvalue_reader = csv.DictReader(pvalue_file, delimiter=delimiter)
#
#                 # Get the header fields from the main CSV.
#                 main_fields = main_reader.fieldnames  # e.g. [var1, accuracy, min, max, var2, var3, ...]
#                 if main_fields is None or len(main_fields) < 5:
#                     raise CommandError("Main CSV file does not have the expected format.")
#
#                 # Loop through both files simultaneously
#                 for main_row, pvalue_row in zip(main_reader, pvalue_reader):
#                     var1 = main_row[main_fields[0]]
#                     if not var1:
#                         continue
#
#                     try:
#                         accuracy = float(main_row.get('accuracy', 0))
#                     except Exception:
#                         accuracy = 0
#
#                     try:
#                         min_val = float(main_row.get('min', 0))
#                     except Exception:
#                         min_val = None
#
#                     try:
#                         max_val = float(main_row.get('max', 0))
#                     except Exception:
#                         max_val = None
#
#                     # Process each correlation column (assume columns 5 onward are correlation values)
#                     for col in main_fields[4:]:
#                         try:
#                             correlation = float(main_row[col])
#                         except Exception:
#                             correlation = None
#
#                         # Look up the corresponding pvalue in the pvalue CSV row.
#                         # (pvalue CSV is assumed to have the same key in the first column and the same variable headers starting at column 2)
#                         if col in pvalue_row:
#                             try:
#                                 pvalue = float(pvalue_row.get(col))
#                             except Exception:
#                                 pvalue = None
#                         else:
#                             pvalue = None
#
#                         # Create a new record for this combination.
#                         TissueCorrelation.objects.create(
#                             from_tissue=from_tissue,
#                             to_tissue=to_tissue,
#                             var1=var1,
#                             var2=col,
#                             correlation=correlation,
#                             pvalue=pvalue,
#                             accuracy=accuracy,
#                             min=min_val,
#                             max=max_val
#                         )
#
#                         inserted_count += 1
#                         if inserted_count % 1000 == 0:
#                             self.stdout.write(f"Inserted {inserted_count} records so far...")
#
#                         if inserted_count >= max_inserts:
#                             self.stdout.write(self.style.SUCCESS("Inserted 100M records so far... shutting down."))
#                             return
#
#         except Exception as e:
#             raise CommandError(f"Error processing CSV files: {e}")
#
#         self.stdout.write(self.style.SUCCESS("Data imported successfully."))

from django.core.management.base import BaseCommand, CommandError
import csv
from Avapp.models import TissueCorrelation
from django.db import transaction

class Command(BaseCommand):
    help = 'Import tissue CSV data with corresponding pvalues, stopping after 100M records.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            help='Path to the main CSV file (e.g., ileum_to_ileum.csv)'
        )
        parser.add_argument(
            'pvalue_csv_path',
            type=str,
            help='Path to the pvalue CSV file (e.g., ileum_to_ileum_pvalue.csv)'
        )
        parser.add_argument(
            '--from_tissue',
            type=str,
            required=True,
            help='Name of the source tissue'
        )
        parser.add_argument(
            '--to_tissue',
            type=str,
            required=True,
            help='Name of the destination tissue'
        )
        parser.add_argument(
            '--delimiter',
            type=str,
            default=',',
            help='CSV delimiter (default is ",")'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        pvalue_csv_path = options['pvalue_csv_path']
        from_tissue = options['from_tissue']
        to_tissue = options['to_tissue']
        delimiter = options['delimiter']

        self.stdout.write(f"Importing main data from: {csv_path}")
        self.stdout.write(f"Importing pvalues from: {pvalue_csv_path}")
        self.stdout.write(f"Tissue relation: {from_tissue} -> {to_tissue}")

        max_inserts = 101000000  # Stop after 100M records
        inserted_count = 0
        batch_size = 1000  # You can adjust the batch size based on your memory/performance needs
        tissue_correlations = []

        try:
            with open(csv_path, newline='', encoding='utf-8') as main_file, \
                 open(pvalue_csv_path, newline='', encoding='utf-8') as pvalue_file:

                main_reader = csv.DictReader(main_file, delimiter=delimiter)
                pvalue_reader = csv.DictReader(pvalue_file, delimiter=delimiter)

                # Validate header of the main CSV
                main_fields = main_reader.fieldnames
                if main_fields is None or len(main_fields) < 5:
                    raise CommandError("Main CSV file does not have the expected format.")

                # Wrap the database operations in a single transaction for performance and consistency.
                with transaction.atomic():
                    # Loop through both files simultaneously
                    for main_row, pvalue_row in zip(main_reader, pvalue_reader):
                        var1 = main_row[main_fields[0]]
                        if not var1:
                            continue

                        try:
                            accuracy = float(main_row.get('accuracy', 0))
                        except Exception:
                            accuracy = 0.0

                        try:
                            min_val = float(main_row.get('min', 0))
                        except Exception:
                            min_val = None

                        try:
                            max_val = float(main_row.get('max', 0))
                        except Exception:
                            max_val = None

                        # Process each correlation column (assuming columns from index 4 onward)
                        for col in main_fields[4:]:
                            try:
                                correlation = float(main_row[col])
                            except Exception:
                                correlation = None

                            # Look up the corresponding pvalue in the pvalue CSV row.
                            if col in pvalue_row:
                                try:
                                    pvalue = float(pvalue_row.get(col))
                                except Exception:
                                    pvalue = None
                            else:
                                pvalue = None

                            tissue_correlations.append(
                                TissueCorrelation(
                                    from_tissue=from_tissue,
                                    to_tissue=to_tissue,
                                    var1=var1,
                                    var2=col,
                                    correlation=correlation,
                                    pvalue=pvalue,
                                    accuracy=accuracy,
                                    min=min_val,
                                    max=max_val
                                )
                            )
                            inserted_count += 1

                            # When we hit the batch size, bulk insert and clear the list.
                            if inserted_count % batch_size == 0:
                                TissueCorrelation.objects.bulk_create(tissue_correlations, batch_size=batch_size)
                                tissue_correlations = []
                                self.stdout.write(f"Inserted {inserted_count} records so far...")

                            if inserted_count >= max_inserts:
                                self.stdout.write(self.style.SUCCESS("Inserted 100M records so far... shutting down."))
                                return

                    # Insert any remaining records that didn't fill up the last batch.
                    if tissue_correlations:
                        TissueCorrelation.objects.bulk_create(tissue_correlations, batch_size=batch_size)

        except Exception as e:
            raise CommandError(f"Error processing CSV files: {e}")

        self.stdout.write(self.style.SUCCESS("Data imported successfully."))
