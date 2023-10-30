
package brokenrobotgame;

import brokenrobotgame.model.GameModel;
import brokenrobotgame.view.GameFieldPanel;
import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;



public class BreakRobotGame extends JFrame {

    private GameModel _model;
    
    private GameFieldPanel _gamePanel;
    
    //===================================================================== main
    public static void main(String[] args) {

        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                new BreakRobotGame();
            }
        });
    }
    
    //============================================================== constructor
    public BreakRobotGame() {
        
        this.setTitle("Сломанный робот");
        
        _model = new GameModel();
        _model.start();
        _gamePanel = new GameFieldPanel(_model);
        
//        //... Create button and check box.
//        JButton newGameBtn = new JButton("Новая игра");
//        newGameBtn.addActionListener(new ActionNewGame());
        
        //... Do layout
        JPanel controlPanel = new JPanel(new FlowLayout());
//        controlPanel.add(newGameBtn);
        
        //... Create content pane with graphics area in center (so it expands)
        JPanel content = new JPanel();
        content.setLayout(new BorderLayout());
        content.add(controlPanel, BorderLayout.NORTH);
        content.add(_gamePanel, BorderLayout.CENTER);
        
        //... Set this window's characteristics.
        setContentPane(content);
        setTitle("Сломанный робот");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        pack();
        setLocationRelativeTo(null);
        setResizable(false);
        setVisible(true);

        _gamePanel.setFocusable(true);
        _gamePanel.setVisible(true);        
}
    
    ////////////////////////////////////////////////////////////// ActionNewGame
    class ActionNewGame implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent evt) {
            _model.start();
        }
    }    
}
