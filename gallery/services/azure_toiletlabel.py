import os
from azure.data.tables import TableServiceClient

class AzureToiletLabelService:
    def __init__(self):
        self.connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        self.table_name = "ToiletLabels"
        self.service_client = TableServiceClient.from_connection_string(self.connection_string)
        self.table_client = self.service_client.get_table_client(self.table_name)
        try:
            self.table_client.create_table()
        except Exception as e:
            print(f"[AzureToiletLabelService] Table creation failed or already exists: {e}")

    def upsert_label(self, label_id, place, description, men_image_url, women_image_url, num_voters, avg_vote):
        entity = {
            'PartitionKey': 'label',
            'RowKey': str(label_id),
            'Place': place,
            'Description': description,
            'MenImageUrl': men_image_url,
            'WomenImageUrl': women_image_url,
            'NumVoters': num_voters,
            'AvgVote': avg_vote,
        }
        self.table_client.upsert_entity(entity=entity)

    def get_label(self, label_id):
        try:
            entity = self.table_client.get_entity(partition_key='label', row_key=str(label_id))
            return entity
        except Exception:
            return None

    def list_labels(self):
        return list(self.table_client.query_entities("PartitionKey eq 'label'"))
