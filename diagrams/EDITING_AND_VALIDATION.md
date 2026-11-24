# Editable UML delivery

All eight original filenames are retained under drawio. Every classifier, state, actor, line and text label is an independent native mxGraph cell. PNG exports include the native XML as metadata; the drawio files remain the authoritative editable sources. Each diagram also has a separately generated vector PDF. No raster screenshot is substituted for the editable model.

Diagrams 01 and 02 share 72 direct, nested-numbered messages across the four required processes. Diagram 01 includes guarded fragments, actors, activations, synchronous calls, asynchronous notifications and returns. Diagram 02 labels directed object links rather than relying on a message catalogue. Diagram 03 preserves the approval gate and immutable regeneration history. Diagram 04 distinguishes stored states, derived expiry conditions and a renewal event that creates new objects.

Diagram 05 attaches common access/data dependencies at a logical package boundary. Diagrams 06-08 use focused packages, class compartments and endpoint multiplicities. Module stereotypes map service names to actual Python modules. Submission is a stable student-assessment anchor; SubmissionAttempt records multiple tries. Grade retains the original first-attempt record and AttemptGrade stores later marks. Diagram notes distinguish logical service associations from actual ORM foreign keys.

The proposal includes enlarged continuation views and package inserts. Broad comprehensive diagrams serve as overviews; use the enlarged inserts or vector zoom to read dense process detail. Headers repeated on continuation extracts do not change the native diagrams.

Validation covers XML structure, editable vertices/edges, endpoint references, direct message consistency, text wrapping bounds, valid PNGs and vector PDFs. The online native editor embed was attempted but timed out after 45 seconds before initializing; no file was loaded. Opening and editing in actual diagrams.net is therefore unverified. Open each drawio file on the presentation computer and use the supplied exporters if network restrictions prevent native PDF export.

```powershell
python -m pip install -r scripts/artifact-requirements.txt
python scripts/generate_uml.py
python scripts/check_interactions.py
python scripts/check_diagram_layout.py
```
