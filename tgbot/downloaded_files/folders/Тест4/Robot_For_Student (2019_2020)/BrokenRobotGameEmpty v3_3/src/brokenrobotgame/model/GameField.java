package brokenrobotgame.model;

import brokenrobotgame.model.navigation.MiddlePosition;
import brokenrobotgame.model.navigation.CellPosition;
import java.util.ArrayList;


/*
 * GameField - абстракция поля, состоящего из ячеек;  
 * контейнер для игровых юнитов (робота, стен и батареек)
 */
public class GameField {

    // ------------------------------ Размеры ---------------------------
	
    public GameField (){
    
        setSize(10, 10);
    }
        
    public final void setSize(int width, int height) {
        CellPosition.setHorizontalRange(1, width);
        CellPosition.setVerticalRange(1, height);
    }

    public int width() {
        return CellPosition.horizontalRange().length();
    }

    public int height() {
        return CellPosition.verticalRange().length();
    }
	
    // ---------------------------- Робот ----------------------------

    !!!
    
    public Robot robot(){
        !!!
    }
    
    !!!
	
    // ---------------------------- Стены ----------------------------

    private ArrayList<WallPiece> _wallPool = new ArrayList();   // стены

    public boolean isWall(MiddlePosition pos){
        
        for (WallPiece obj : _wallPool)
        {
            if(obj.position().equals(pos))  return true;
        }
        
        return false;
    }
    
    public boolean addWall(MiddlePosition pos, WallPiece obj){
        
        boolean success = obj.setPosition(pos);
        
        if(success) _wallPool.add(obj);
        
        return success;
    }

    // ---------------------------- Двери ----------------------------

    private ArrayList<Door> _doorPool = new ArrayList();        // двери

    public Door door(MiddlePosition pos){
        
        for (Door obj : _doorPool)
        {
            if(obj.position().equals(pos))  return obj;
        }
        
        return null;
    }
    
    public boolean addDoor(MiddlePosition pos, Door obj){
        
        boolean success = obj.setPosition(pos);
        
        if(success) _doorPool.add(obj);
        
        return success;
    }
    
    // ---------------------------- Батарейки ----------------------------
    
    private ArrayList<Battery> _batteryPool = new ArrayList();  // батарейки

    public Battery battery(CellPosition pos){
        
        for (Battery obj : _batteryPool)
        {
            if(obj.position().equals(pos))  return obj;
        }
        
        return null;
    }
	
    public boolean addBattery(CellPosition pos, Battery obj){
        
        boolean success = obj.setPosition(pos);
        
        if(success) _batteryPool.add(obj);
        
        return success;
    }
    
    public boolean removeBattery(Battery obj){
        
        boolean success = _batteryPool.remove(obj);
        
        if(success) obj.setPosition(null);
        
        return success;
    }
    
    // ---------------------------- Очистка ----------------------------
    
    public void clear()
    {
        !!!
        _wallPool.clear();
        _batteryPool.clear();
    }
}