# Diagram validation evidence

All eight `.drawio` files contain native uncompressed `mxfile/mxGraphModel`
documents, independent vertices, connectors, labels, geometry and valid endpoint
references. No raster image replaces a UML source diagram. `validation.json`
records the editable vertex/edge counts and exported dimensions for each file.

`scripts/generate_uml.py` validates the saved XML and exports the supported
primitives to PNG and vector PDF from that same XML. PNG metadata also retains
the source XML. The source diagrams remain the editing authority. Each process
frame in the sequence and communication views shares one message definition.

Visual review corrected reversed transition attachment ports, connectors crossing
class text, package-label placement, separate Grade/Submission classes and proper
alt/opt/loop interaction frames. Package relationship catalogues state endpoint
multiplicities; module stereotypes identify services implemented as Python modules.

The native online editor was also attempted using draw.io's documented embed
load/export API. It timed out after 45 seconds waiting for its initialization
event; it never reached the load step. This is not evidence that the XML failed to
decode, and it is not counted as a successful native-editor opening check.

To repeat on a connected computer, run the application locally and execute
`node scripts/validate_drawio.mjs` after `npm ci` in frontend. It loads every source
with editing enabled and requests native SVG/PNG exports. Alternatively, open
each `.drawio` file in diagrams.net or the desktop draw.io application and verify
that individual class boxes, messages and transition labels can be selected.

Reference: https://www.drawio.com/docs/reference/embed-mode/
