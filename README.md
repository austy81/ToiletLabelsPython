# ToiletLabelsPython
Reincarnation of my university time idea using Django.

Project is basically galery of images of toilet signs. It is always pair of images - one for men and one for women.

There will be admin which can upload images (always one for man one for woman). Fill in name of place, coordinates and description.

Images will be stored in Azure Blob storage.

## Deployment

az ad sp create-for-rbac --name "toiletlabels-github" --role contributor \
       --scopes /subscriptions/b355f86c-94b4-467b-b643-1206cbf0e24c/resourceGroups/ToiletLabels/providers/Microsoft.Web/sites/toiletlabels
     ```
   - Replace `{subscription-id}` with your Azure subscription ID and `{resource-group}` with your resource group name
   - The command will output JSON similar to this:
     ```json
{
  "appId": "9e8467da-efb0-4b29-8f8b-64fc81060770",
  "displayName": "toiletlabels-github",
  "password": "?",
  "tenant": "7fb36e64-7955-42a3-807a-ffba7c00f6d7"
}
     ```
   - You need to transform this output into the format required by the GitHub Actions Azure login. Add it to the secrets in the repository as `AZURE_CREDENTIALS`:
     ```json
{
    "clientId": "9e8467da-efb0-4b29-8f8b-64fc81060770",
    "clientSecret": "?",
    "tenantId": "7fb36e64-7955-42a3-807a-ffba7c00f6d7",
    "subscriptionId": "b355f86c-94b4-467b-b643-1206cbf0e24c"
}
     ```