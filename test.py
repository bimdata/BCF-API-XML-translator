from bcf_api_xml import import_zip

# import_zip.import_bcf_zip(
#     "/home/amoki/Downloads/BIMcollab/01_Test de masse/01_CRM_AnalyseMaquette_crit1a7.bcf"
# )

# import_zip.import_bcf_zip("/home/amoki/Downloads/test_MAP_2.bcf")
topics = import_zip.import_bcf_zip(
    "/home/amoki/Downloads/Solibri/01_Test de masse/BIM IN MOTION_APS_v2.bcf"
)
print(topics)
