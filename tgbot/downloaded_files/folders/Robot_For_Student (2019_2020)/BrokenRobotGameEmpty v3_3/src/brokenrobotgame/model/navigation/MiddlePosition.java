package brokenrobotgame.model.navigation;

/*
 * Позиция на стыке двух ячеек
 */
public class MiddlePosition
{
    // ---------------------------------------------------------------------
    /* Определяем как позицию ячейки и направление от нее. 
     В нормализованном виде используются только направления "запад" и "север", 
     кроме крайних позиций справа и снизу поля */
    // ---------------------------------------------------------------------
    
    private CellPosition _cellPosition; 
    private Direction _direction;  			
    

    public Direction direction(){
        return _direction;
    }
    
    public CellPosition cellPosition(){
        return _cellPosition;
    }
    
    // ------------------ Порождение "средних" позиций ---------------------

    public MiddlePosition(CellPosition cellPos, Direction direct){
        
        if(!cellPos.isValid())
        {
            // ТODO породить исключение
        }    
        
        _cellPosition = cellPos;
        _direction = direct;
                
        normalize();
}

    private void normalize() {
       
        // По возможности приводим к направлению "север"
        if(_direction.equals(Direction.south()) && _cellPosition.hasNext(_direction))
        {
            _cellPosition = _cellPosition.next(_direction);
            _direction = Direction.north();
        }
        
        // Приводим к направлению "запад"
        if(_direction.equals(Direction.east()) && _cellPosition.hasNext(_direction))
        {
            _cellPosition = _cellPosition.next(_direction);
            _direction = Direction.west();
        }
    }

    @Override
    public MiddlePosition clone(){ 
        return new MiddlePosition(_cellPosition, _direction); 
    }

    
    public MiddlePosition next(Direction direct){
		
	// В заданном направлении имеется ячейка
	if(_cellPosition.hasNext(direct))
	{
            return new MiddlePosition(_cellPosition.next(direct), _direction);
	}
		
	// В заданном направлении нет ячейки, но у крайней ячейки имеется вторая "средняя" позиция
	if(_direction.isOpposite(direct))
	{
            return  new MiddlePosition(_cellPosition, _direction.opposite());
	}
		
	// TODO породить исключение
        return null;
    }

    public boolean hasNext(Direction direct){
	return _cellPosition.hasNext(direct) || _direction.isOpposite(direct);
    }
	

    // ------------------ Порождение позиций ячеек ---------------------
	
    public CellPosition cellPosition(Direction direct){
		
        // Уже находимся в ячейке
	if(_direction.isOpposite(direct))
	{
            return _cellPosition.clone();
	}
		
	// Необходимо получить другую ячейку
	if(_direction.equals(direct) && _cellPosition.hasNext(direct))
	{
            return _cellPosition.next(direct);
	}
		
	// TODO Породить исключение
        return null;
}

	public boolean hasCellPosition(Direction direct){
            return _direction.isOpposite(direct) || _cellPosition.hasNext(direct);
	}
        
    // ------------------ Сравнение позиций ---------------------
    
    public boolean equals(Object other){
        
        if(other instanceof MiddlePosition) {
            // Типы совместимы, можно провести преобразование
            MiddlePosition otherPosition = (MiddlePosition)other;
            
            // Описание позиций совпадает
            return _cellPosition.equals(otherPosition._cellPosition) && _direction.equals(otherPosition._direction);
        }
        
        return false;
    }
	
//    @Override
//    public int hashCode(){
//        // TODO
//        return _direction.hashCode()*_cellPosition.hashCode();
//    }
}