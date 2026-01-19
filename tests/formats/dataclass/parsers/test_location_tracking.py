"""Tests for XML location tracking feature."""
from unittest import TestCase

from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig


class LocationTrackingTests(TestCase):
    """Test location tracking functionality."""

    def test_location_tracking_disabled_by_default(self) -> None:
        """Test that location tracking is disabled by default."""
        config = ParserConfig()
        self.assertFalse(config.location_tracking)

    def test_location_tracking_can_be_enabled(self) -> None:
        """Test that location tracking can be enabled."""
        config = ParserConfig(location_tracking=True)
        self.assertTrue(config.location_tracking)

    def test_location_not_set_when_tracking_disabled(self) -> None:
        """Test that location is not set when tracking is disabled."""
        from tests.fixtures.primer import PurchaseOrder

        config = ParserConfig(location_tracking=False)
        context = XmlContext()
        parser = XmlParser(context=context, config=config)
        order = parser.parse("tests/fixtures/primer/sample.xml", PurchaseOrder)

        self.assertFalse(hasattr(order, "_xml_location_"))
        self.assertFalse(hasattr(order.bill_to, "_xml_location_"))
        self.assertFalse(hasattr(order.ship_to, "_xml_location_"))

    def test_location_set_when_tracking_enabled_with_lxml(self) -> None:
        """Test that location is set when tracking is enabled (lxml handler)."""
        try:
            import lxml  # noqa: F401
        except ImportError:
            self.skipTest("lxml not available")

        from tests.fixtures.primer import PurchaseOrder

        config = ParserConfig(location_tracking=True)
        context = XmlContext()
        parser = XmlParser(context=context, config=config)
        order = parser.parse("tests/fixtures/primer/sample.xml", PurchaseOrder)

        # Verify location is set on the parsed objects
        self.assertTrue(hasattr(order, "_xml_location_"))
        self.assertEqual(2, order._xml_location_)  # <purchaseOrder> on line 2

        self.assertTrue(hasattr(order.ship_to, "_xml_location_"))
        self.assertEqual(3, order.ship_to._xml_location_)  # <shipTo> on line 3

        self.assertTrue(hasattr(order.bill_to, "_xml_location_"))
        self.assertEqual(10, order.bill_to._xml_location_)  # <billTo> on line 10

        self.assertTrue(hasattr(order.items, "_xml_location_"))
        self.assertEqual(18, order.items._xml_location_)  # <items> on line 18

        # Check nested items
        self.assertEqual(2, len(order.items.item))
        self.assertTrue(hasattr(order.items.item[0], "_xml_location_"))
        self.assertEqual(19, order.items.item[0]._xml_location_)  # First <item> on line 19

        self.assertTrue(hasattr(order.items.item[1], "_xml_location_"))
        self.assertEqual(25, order.items.item[1]._xml_location_)  # Second <item> on line 25

    def test_location_not_set_with_native_handler(self) -> None:
        """Test that location is not set with native handler (no sourceline)."""
        from xsdata.formats.dataclass.parsers.handlers import XmlEventHandler
        from tests.fixtures.primer import PurchaseOrder

        # Force use of native handler even if lxml is available
        config = ParserConfig(location_tracking=True)
        context = XmlContext()
        parser = XmlParser(context=context, config=config, handler=XmlEventHandler)
        order = parser.parse("tests/fixtures/primer/sample.xml", PurchaseOrder)

        # Native handler doesn't provide sourceline, so location should not be set
        self.assertFalse(hasattr(order, "_xml_location_"))
        self.assertFalse(hasattr(order.bill_to, "_xml_location_"))
        self.assertFalse(hasattr(order.ship_to, "_xml_location_"))

    def test_location_tracking_with_from_string(self) -> None:
        """Test location tracking works with from_string."""
        try:
            import lxml  # noqa: F401
        except ImportError:
            self.skipTest("lxml not available")

        from tests.fixtures.primer import PurchaseOrder

        xml_content = """<?xml version="1.0" ?>
<purchaseOrder orderDate="1999-10-20">
  <shipTo country="US">
    <name>Alice Smith</name>
    <street>123 Maple Street</street>
    <city>Mill Valley</city>
    <state>CA</state>
    <zip>90952</zip>
  </shipTo>
  <billTo country="US" type="">
    <name>Robert Smith</name>
    <street>8 Oak Avenue</street>
    <city>Old Town</city>
    <state>PA</state>
    <zip>95819</zip>
  </billTo>
  <comment>Hurry, my lawn is going wild!</comment>
  <items>
    <item partNum="872-AA">
      <productName>Lawnmower</productName>
      <quantity>1</quantity>
      <USPrice>148.95</USPrice>
      <comment>Confirm this is electric</comment>
    </item>
  </items>
</purchaseOrder>
"""
        config = ParserConfig(location_tracking=True)
        context = XmlContext()
        parser = XmlParser(context=context, config=config)
        order = parser.from_string(xml_content, PurchaseOrder)

        # Verify location is set
        self.assertTrue(hasattr(order, "_xml_location_"))
        self.assertEqual(2, order._xml_location_)

        self.assertTrue(hasattr(order.ship_to, "_xml_location_"))
        self.assertEqual(3, order.ship_to._xml_location_)

        self.assertTrue(hasattr(order.bill_to, "_xml_location_"))
        self.assertEqual(10, order.bill_to._xml_location_)
