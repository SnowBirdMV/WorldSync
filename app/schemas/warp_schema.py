"""
app/schemas/warp_schema.py

Defines Marshmallow schemas for validating and deserializing data related to warps/waypoints.
"""

from marshmallow import Schema, fields


class WarpSchema(Schema):
    name = fields.Str(required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    z = fields.Float(required=True)
    dimension = fields.Str(required=True)
