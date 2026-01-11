import os
import sys
import unittest


class TestProcessorSimple(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # initialize QGIS
        from qgis.core import QgsApplication
        QgsApplication.setPrefixPath("/usr", True)
        cls.app = QgsApplication([], False)
        cls.app.initQgis()

        # import processor
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from processor import Processor
        cls.processor = Processor()
        cls.test_layer = cls.processor.load_layer("./test_data.geojson")

    @classmethod
    def tearDownClass(cls):
        from qgis.core import QgsProject
        QgsProject.instance().removeAllMapLayers()
        cls.app.exitQgis()

    def test_1_load_layer(self):
        """test 1: loading a layer"""
        from qgis.core import QgsVectorLayer, QgsProject
        self.assertIsInstance(self.test_layer, QgsVectorLayer)
        self.assertEqual(self.test_layer.featureCount(), 7)
        self.assertEqual(self.test_layer.crs().authid(), "EPSG:4326")

        project_layers = QgsProject.instance().mapLayers()
        self.assertGreater(len(project_layers), 0)

    def test_2_filter_features(self):
        """test 2: filtering objects"""
        filtered = self.processor.filter_features(self.test_layer, "population >= 1000")
        self.assertEqual(len(filtered), 4)
        populations = [f['population'] for f in filtered]
        self.assertIn(2500, populations)
        self.assertIn(3200, populations)
        self.assertIn(1200, populations)
        self.assertIn(1000, populations)

    def test_3_create_buffer_layer(self):
        """test 3: creating a buffer layer"""
        filtered = self.processor.filter_features(self.test_layer, "population >= 1000")

        # create temporary layer
        from qgis.core import QgsVectorLayer
        temp_layer = QgsVectorLayer(
            f"Polygon?crs={self.test_layer.crs().authid()}", "temp", "memory"
        )
        temp_layer.dataProvider().addAttributes(self.test_layer.fields())
        temp_layer.updateFields()
        temp_layer.dataProvider().addFeatures(filtered)

        # test buffer creation
        buffer_layer = self.processor.create_buffer_layer(temp_layer, 1000)

        # checks
        self.assertIsNotNone(buffer_layer)
        from qgis.core import QgsVectorLayer
        self.assertIsInstance(buffer_layer, QgsVectorLayer)
        self.assertEqual(buffer_layer.featureCount(), 4)

        # check if layer added to project
        from qgis.core import QgsProject
        layers = QgsProject.instance().mapLayersByName("buffered_cities")
        self.assertEqual(len(layers), 1)

    def test_4_full_pipeline(self):
        """test 4: full processing pipeline"""
        result = self.processor.full_pipeline("./test_data.geojson")
        self.assertIsNotNone(result)

        # check result is a layer
        from qgis.core import QgsVectorLayer
        self.assertIsInstance(result, QgsVectorLayer)

        self.assertEqual(result.featureCount(), 4)

    def test_5_transform_coordinates(self):
        """test 5: coordinate transformation"""
        transformed = self.processor.transform_coordinates(self.test_layer)
        from qgis.core import QgsVectorLayer
        self.assertIsInstance(transformed, QgsVectorLayer)
        self.assertEqual(transformed.crs().authid(), "EPSG:7683")  # GSK-2011
        self.assertEqual(transformed.featureCount(), 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)