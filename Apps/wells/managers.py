from django.db import models

class WellManager(models.Manager):

    def search_type_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).values("PumpType")
        return result[0]

    def search_id_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).values("id").first()
        return result

    def search_info_pump(self, wellName):
        result = self.filter(
            PumpName=wellName
        ).first()
        return result
    
    def search_all_pump(self, company):
        result = self.filter(
            UserAuthor__CompanyName = company
        ).values("id",
                 "PumpName",
                 "FieldName__FieldName",
                 "BatteryName__BatteryName",
                 "GroupName__GroupName",
                 "StrokeLength",
                 "MotorType",
                 "PolishedRodDiameter",
                 "PumpIntake",
                 "PlungerDiameter",
                 "TrueVerticalDepth",
                 "TotalRodLength",
                 "TotalRodWeight"
                 )
        return result


