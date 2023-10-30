package brokenrobotgame.model;

import brokenrobotgame.model.events.RobotActionEvent;
import brokenrobotgame.model.events.RobotActionListener;
import brokenrobotgame.model.navigation.CellPosition;
import brokenrobotgame.model.navigation.Direction;
import brokenrobotgame.model.navigation.MiddlePosition;

/*
 * GameModel - абстракция всей игры; генерирует стартовую обстановку; 
 * следит за роботом с целью определения конца игры
 */
public class GameModel {

    // ----------------------- Игровое поле и робот на нем ------------------
    GameField _field = new GameField();
    
    public GameField field(){
        return _field;
    }
    
    !!!
    
    public Robot robot(){
        !!!
    }

    public void start(){
        generateField();
        
        // Вдруг игра завершилась, еще не начавшись
        identifyGameOver();
        
        // "Следим" за роботом
        !!!
    }
    
    // -------------------- Целевая позиция робота --------------------------
    CellPosition _targetPos;
    
    public CellPosition targetPosition(){
        return _targetPos;
    }
    
    // ------------ Задаем обстановку и следим за окончанием игры  ------------

    private void generateField(){

        // Обстановка = робот+стены+батарейка на поле+двери
        !!!
        _field.addWall(new MiddlePosition(robot().position(), Direction.east()), new WallPiece(_field));
        _field.addWall(new MiddlePosition(robot().position(), Direction.south()), new WallPiece(_field));
        Battery outBattery = new Battery(_field, 5, 3);
        _field.addBattery(new CellPosition(2, 1), outBattery);
        //_field.addBattery(robot().position().next(Direction.south()).next(Direction.south()), outBattery);
        _field.addDoor(new MiddlePosition(new CellPosition(5, 4), Direction.east()), new Door(_field));
        _field.addDoor(new MiddlePosition(new CellPosition(1, 1), Direction.north()), new Door(_field));
        
        
        // Целевая позиция рядом с роботом
        _targetPos = robot().position().next(Direction.west());
    }
    
    private void identifyGameOver(){
        
        if(robot().position().equals(_targetPos))
        {
            System.out.println("You reach target position!!!");
        }
        else if(robot().amountОfСharge()==0)
        {
            System.out.println("You amount of charge is null!!!");
        }
    }   
    
    private class RobotObserver implements RobotActionListener{

        @Override
        public void robotMakedMove(RobotActionEvent e) {
            identifyGameOver();
        }
    }
}
