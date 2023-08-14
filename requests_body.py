get_brands = {"getArticles": {
            "arg0": {"perPage": 0, "articleCountry": "RU", "lang": "ru", "provider": 2387, "linkageTargetId": 0,
                     "linkageTargetType": "U", "filterQueries": [f"(dataSupplierId NOT IN ({4978},{4982}))"],
                     "assemblyGroupFacetOptions": {"enabled": 'true'}, "includeDataSupplierFacets": 'true',
                     "includeGenericArticleFacets": 'true'}}}


get_nameGroups_idGroups = {
            "getArticles": {
                "arg0": {
                    "articleCountry": "RU",
                    "provider": 2387,
                    "lang": "ru",
                    "includeAll": 'false',
                    "includeLinkages": 'false',
                    "includeGenericArticles": 'false',
                    "includeArticleCriteria": 'false',
                    "includeMisc": 'false',
                    "includeImages": 'false',
                    "includeArticleText": 'false',
                    "includeOEMNumbers": 'false',
                    "includeReplacedByArticles": 'false',
                    "includeReplacesArticles": 'false',
                    "filterQueries": [
                        f"(dataSupplierId NOT IN ({4978},{4982}))"
                    ],
                    "includeGTINs": 'false',
                    "includeTradeNumbers": 'false',
                    "includeDataSupplierFacets": 'true',
                    "includeGenericArticleFacets": 'true',
                    "includeCriteriaFacets": 'false',
                    "page": 1,
                    "perPage": 0,
                    "sort": 'null'
                }
            }
        }

get_articles_list = {
                   "getArticles": {
                      "arg0": {
                         "articleCountry": "PL",
                         "provider": 2387,
                         "lang": "ru",
                         "sort": [
                            {
                               "field": "score",
                               "direction": "desc"
                            },
                            {
                               "field": "mfrName",
                               "direction": "asc"
                            },
                            {
                               "field": "linkageSortNum",
                               "direction": "asc"
                            }
                         ],
                         "filterQueries": [
                            f"(dataSupplierId NOT IN ({4978},{4982}))"
                         ],
                         "criteriaFilters": [],
                         "articleStatusIds": [],
                         "includeAll": 'false',
                         "includeLinkages": 'true',
                         "linkagesPerPage": 100,
                         "includeGenericArticles": 'true',
                         "includeArticleCriteria": 'true',
                         "includeMisc": 'true',
                         "includeImages": 'true',
                         "includePDFs": 'true',
                         "includeLinks": 'true',
                         "includeArticleText": 'true',
                         "includeOEMNumbers": 'true',
                         "includeReplacedByArticles": 'true',
                         "includeReplacesArticles": 'true',
                         "includeComparableNumbers": 'true',
                         "includeGTINs": 'true',
                         "includeTradeNumbers": 'true',
                         "includePrices": 'false',
                         "includePartsListArticles": 'false',
                         "includeAccessoryArticles": 'false',
                         "includeArticleLogisticsCriteria": 'true',
                         "includeDataSupplierFacets": 'true',
                         "includeGenericArticleFacets": 'true',
                         "includeArticleStatusFacets": 'true',
                         "includeCriteriaFacets": 'true'
                      }
                   }
                }

get_article_details = {
           "getArticles": {
              "arg0": {
                 "articleCountry": "PL",
                 "provider": 2387,
                 "lang": "ru",
                 "searchMatchType": "exact",
                 "searchType": 0,
                 "page": 1,
                 "perPage": 10,
                 "filterQueries": [
                     f"(dataSupplierId NOT IN ({4978},{4982}))"
                 ],
                 "includeAll": 'false',
                 "includeLinkages": 'true',
                 "linkagesPerPage": 100,
                 "includeGenericArticles": 'true',
                 "includeArticleCriteria": 'true',
                 "includeMisc": 'true',
                 "includeImages": 'true',
                 "includePDFs": 'true',
                 "includeLinks": 'true',
                 "includeArticleText": 'true',
                 "includeOEMNumbers": 'true',
                 "includeReplacedByArticles": 'true',
                 "includeReplacesArticles": 'true',
                 "includeComparableNumbers": 'true',
                 "includeGTINs": 'true',
                 "includeTradeNumbers": 'true',
                 "includePrices": 'true',
                 "includePartsListArticles": 'true',
                 "includeAccessoryArticles": 'true',
                 "includeArticleLogisticsCriteria": 'true',
                 "includeDataSupplierFacets": 'true',
                 "includeGenericArticleFacets": 'true',
                 "includeCriteriaFacets": 'true'
              }
           }
        }

get_related_vehicles = {
            "getArticleLinkedAllLinkingTargetManufacturer2": {
                "arg0": {
                    "provider": 2387,
                    "articleCountry": "PL",
                    "country": "RU",
                    "countryGroupFlag": 'false',
                    "linkingTargetType": "VOLB"
                }
            }
        }

get_vehicle_id = {
           "getArticleLinkedAllLinkingTarget4": {
              "arg0": {
                 "provider": 2387,
                 "lang": "ru",
                 "articleCountry": "PL",
                 "country": "RU",
                 "countryGroupFlag": 'false',
                 "linkingTargetType": "VOLB",
                 "withMainArticles": 'false'
                        }
                    }
                 }

get_car_manufacturers = {
   "getManufacturers2": {
      "arg0": {
         "lang": "ru",
         "country": "PL",
         "provider": 2387,
         "countryGroupFlag": 'false',
         "linkingTargetType": "V",
         "favouredList": 2
      }
   }
}

get_car_details = {
    "getLinkageTargets": {
        "arg0": {
            "linkageTargetCountry": "PL",
            "linkageTargetCountryGroupFlag": 'false',
            "provider": 2387,
            "lang": "ru",
            "perPage": 100,
            "page": 1
        }
    }
}

get_car_series = {
   "getLinkageTargets": {
      "arg0": {
         "lang": "ru",
         "provider": 2387,
         "linkageTargetCountry": "PL",
         "linkageTargetCountryGroupFlag": 'false',
         "linkageTargetType": "V",
         "includeAllFacets": 'false',
         "includeVehicleModelSeriesFacets": 'true',
         "perPage": 1,
         "filterMode": "preferred"
      }
   }
}