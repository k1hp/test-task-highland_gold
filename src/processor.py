from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFeatureRequest, QgsGeometry,
    QgsFields, QgsField, QgsWkbTypes, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsCoordinateTransformContext, QgsFeature
)
from qgis.PyQt.QtCore import QVariant


class Processor:
    def __init__(self):
        self.project = QgsProject.instance()

    def load_layer(self, file_path):
        """load vector layer from GeoJSON"""
        layer = QgsVectorLayer(file_path, "cities", "ogr")
        if not layer.isValid():
            raise ValueError("failed to load layer")

        self.project.addMapLayer(layer)
        return layer

    def filter_features(self, layer, expression):
        """filter features by expression"""
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        features = [f for f in layer.getFeatures(request)]
        return features

    def transform_coordinates(self, layer):
        """transform coordinates from WGS84 (EPSG:4326) to GSK-2011 (EPSG:7683)"""
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        target_crs = QgsCoordinateReferenceSystem("EPSG:7683")  # GSK-2011

        transform_context = QgsCoordinateTransformContext()
        transform = QgsCoordinateTransform(source_crs, target_crs, transform_context)

        transformed_features = []
        for feature in layer.getFeatures():
            new_feature = QgsFeature(feature)
            geometry = feature.geometry()
            geometry.transform(transform)
            new_feature.setGeometry(geometry)
            transformed_features.append(new_feature)

        # create new layer with transformed coordinates
        transformed_layer = QgsVectorLayer(
            f"Polygon?crs={target_crs.authid()}", "transformed_cities", "memory"
        )
        transformed_layer.dataProvider().addAttributes(layer.fields())
        transformed_layer.updateFields()
        transformed_layer.dataProvider().addFeatures(transformed_features)

        self.project.addMapLayer(transformed_layer)
        return transformed_layer

    def create_buffer_layer(self, layer, distance):
        """create buffer layer"""
        fields = QgsFields()
        fields.append(QgsField("population", QVariant.Int))
        fields.append(QgsField("original_name", QVariant.String))

        crs = layer.crs().authid()
        buffer_layer = QgsVectorLayer(
            f"Polygon?crs={crs}", "buffered_cities", "memory"
        )
        buffer_layer.dataProvider().addAttributes(fields)
        buffer_layer.updateFields()

        features = []
        for feature in layer.getFeatures():
            new_feature = QgsFeature(feature)
            # preserve original name and double population (as in original code)
            new_feature.setAttributes([feature['population'] * 2, feature['name']])
            geom = feature.geometry().buffer(distance, 25)
            new_feature.setGeometry(geom)
            features.append(new_feature)

        buffer_layer.dataProvider().addFeatures(features)
        self.project.addMapLayer(buffer_layer)
        return buffer_layer

    def full_pipeline(self, file_path):
        """full processing pipeline"""
        layer = self.load_layer(file_path)
        filtered_features = self.filter_features(layer, "population >= 1000")

        # create temporary layer from filtered features
        temp_layer = QgsVectorLayer(
            f"Polygon?crs={layer.crs().authid()}", "filtered_temp", "memory"
        )
        temp_layer.dataProvider().addAttributes(layer.fields())
        temp_layer.updateFields()
        temp_layer.dataProvider().addFeatures(filtered_features)

        buffer_layer = self.create_buffer_layer(temp_layer, 1000)
        return buffer_layer


if __name__ == "__main__":
    processor = Processor()
    layer = processor.load_layer("test_data.geojson")
    filtered = processor.filter_features(layer, "population >= 1000")
    print(f"filtered objects: {len(filtered)}")
    buffer_layer = processor.create_buffer_layer(layer, 1000)