package brokenrobotgame.model.navigation;

/*
 * Direction - абстракци€ направлени€ в системе координат "север-юг-восток-запад"; 
 * позвол€ет сравнивать направлени€ и порождать новые направлени€ относительно 
 * текущего
 */
public class Direction {
    
    // определ€ем направление как угол в градусах от 0 до 360
    private int _angle = 90;

    private Direction(int angle) {
        // ѕриводим заданный угол к допустимому диапазону 
        angle = angle%360;
        if(angle < 0)    angle += 360;
        
        this._angle = angle;
    }
    
    // ------------------ ¬озможные направлени€ ---------------------
    
    public static Direction north()
    { return new Direction(90); }
    
    public static Direction south()
    { return new Direction(270); }

    public static Direction east()
    { return new Direction(0); }

    public static Direction west()
    { return new Direction(180); }
    
  
    // ------------------ Ќовые направлени€ ---------------------
    
    @Override
    public Direction clone(){ 
        return new Direction(this._angle); 
    }
  
    public Direction clockwise() { 
        return new Direction(this._angle-90); 
    }
    
    public Direction anticlockwise() { 
        return new Direction(this._angle+90); 
    }
    
    public Direction opposite() { 
        return new Direction(this._angle+180); 
    }
    
    public Direction rightword()  { 
        return clockwise(); 
    }
    
    public Direction leftword()  { 
        return anticlockwise(); 
    }
    
    // ------------------ —равнить направлени€ ---------------------
    
    @Override
    public boolean equals(Object other) {

        if(other instanceof Direction) {
            // “ипы совместимы, можно провести преобразование
            Direction otherDirect = (Direction)other;
            // ¬озвращаем результат сравнени€ углов
            return  _angle == otherDirect._angle;
        }
        
        return false;
    }

    @Override
    public int hashCode() {
        return this._angle;
    }
    
    public boolean isOpposite(Direction other) {
        return this.opposite().equals(other);
    }
}