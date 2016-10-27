package me.lucaspickering.casecontrol.mode.lcd;

import java.awt.Color;

public interface LcdMode {

    /**
     * Initialize this mode using the given arguments.
     *
     * @param args the arguments to initialize with
     */
    void init(String... args);

    /**
     * Gets the {@link EnumLcdMode} for this mode.
     *
     * @return the appropriate {@link EnumLcdMode}
     */
    EnumLcdMode getMode();

    /**
     * Gets the color that the LCD should currently be.
     *
     * @return the desired color
     */
    Color getColor();

    /**
     * Gets the text that should currently be displayed on the LCD. A String in the array CAN be
     * longer than {@link me.lucaspickering.casecontrol.Consts#LCD_WIDTH}, which case the String
     * should be cut down to size by the caller of this method.
     *
     * @return a String[] of length {@link me.lucaspickering.casecontrol.Consts#LCD_HEIGHT}
     */
    String[] getText();

}