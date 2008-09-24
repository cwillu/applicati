sizes = [[None], [None]]
grid = [[None]]  #[x][y]

def split(cell, direction):
  global sizes, grid
  x, y = cell
  dx, dy = direction
  def insert(sizes, grid, cell, direction):    
    x, y = cell
    size = sizes[0][x]
    sizes[0][x:x+1] = [size/2, size/2]
        
    selection = list(grid[x])
    selection[y] = None    
    grid.insert(x + (1 if direction > 0 else 0), selection)
  
  if dx:
    insert(sizes, grid, cell, dx)
    if dx < 0:
      cell = x + 1, y
  if dy:
    _sizes = list(reversed(sizes))
    _grid = zip(*grid)    
    insert(_sizes, _grid, reversed(cell), dy)
    sizes = list(reversed(_sizes))
    grid = zip(*_grid)    


