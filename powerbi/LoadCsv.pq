// Create a text parameter named DemoFolder pointing to the public examples directory.
// This source-level function uses local files only; no corporate path is included.
(FileName as text, ColumnTypes as list) as table =>
let
    Allowed = {"FactDaily.csv", "DimResource.csv", "Snapshot.csv", "Coverage.csv", "DimDate.csv"},
    Checked = if List.Contains(Allowed, FileName) then FileName else error "Unknown demo table",
    Raw = Csv.Document(File.Contents(DemoFolder & "/" & Checked),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, ColumnTypes, "en-US")
in
    Typed
