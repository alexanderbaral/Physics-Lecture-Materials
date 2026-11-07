-- Shared notebook reader for the script and exercise sheets.
-- Outputs and raw cells are not typeset.
local function notebook_cells(path)
    local file = assert(io.open(path, "rb"))
    kpse.record_input_file(path)
    local data = file:read("*a")
    file:close()

    local notebook = utilities.json.tolua(data)
    assert(type(notebook) == "table" and type(notebook.cells) == "table",
        "Expected a Jupyter notebook with a cells array")

    local cells = {}
    local has_code = false
    for _, cell in ipairs(notebook.cells) do
        if cell.cell_type == "code" or cell.cell_type == "markdown" then
            local source = cell.source
            if type(source) == "table" then
                source = table.concat(source)
            end
            assert(type(source) == "string", "Invalid source in a notebook cell")
            if source:find("%S") then
                has_code = has_code or cell.cell_type == "code"
                cells[#cells + 1] = {source = source, kind = cell.cell_type}
            end
        end
    end
    assert(has_code, "Notebook contains no nonempty code cells")
    return cells
end

local next_cell_file = 0

local function write_cell(cell)
    next_cell_file = next_cell_file + 1
    local filename = tex.jobname .. ".notebook-" .. next_cell_file .. ".tmp"
    local directory = status.output_directory
    local path = directory and directory ~= "" and (directory .. "/" .. filename) or filename
    local file = assert(io.open(path, "wb"))
    assert(file:write(cell.source))
    assert(file:close())
    return path
end

local function emit_file(command, ...)
    tex.sprint(command)
    for _, argument in ipairs({...}) do
        tex.sprint("{")
        tex.sprint(-2, argument)
        tex.sprint("}")
    end
end

local function typeset(path)
    local extension = path:lower():match("%.([^./]+)$")
    if extension == "py" then
        emit_file("\\ScriptPythonFile", path)
        return
    end

    assert(extension == "ipynb", "Expected a .py or .ipynb file")
    local notebook_name = path:match("([^/]+)%.[^./]+$")
    for index, cell in ipairs(notebook_cells(path)) do
        local cell_file = write_cell(cell)
        if cell.kind == "code" then
            local name = notebook_name .. "-cell-" .. index .. ".py"
            emit_file("\\ScriptNotebookCodeCell", cell_file, name)
        else
            emit_file("\\ScriptNotebookMarkdownCell", cell_file)
        end
    end
end

return function(path)
    local ok, message = pcall(typeset, path)
    if not ok then
        tex.error("PythonCode: " .. path .. ": " .. tostring(message))
    end
end
