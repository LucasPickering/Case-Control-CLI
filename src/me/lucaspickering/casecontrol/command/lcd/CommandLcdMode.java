package me.lucaspickering.casecontrol.command.lcd;

import java.util.Arrays;

import me.lucaspickering.casecontrol.CaseControl;
import me.lucaspickering.casecontrol.command.AbstractCommand;
import me.lucaspickering.casecontrol.mode.lcd.EnumLcdMode;

public class CommandLcdMode extends AbstractCommand {

    @Override
    public String getName() {
        return "mode";
    }

    @Override
    public String getArgDesc() {
        return "<mode>";
    }

    @Override
    public String getFullDesc() {
        // List all the possible modes
        final CharSequence[] names =
            Arrays.stream(EnumLcdMode.values()).map(m -> m.name).toArray(CharSequence[]::new);
        return "Set the mode for the LCD. Valid modes are: " + String.join(", ", names);
    }

    @Override
    public boolean execute(String[] args) {
        if (args.length >= 1) {
            final String mode = args[0];
            for (EnumLcdMode lcdMode : EnumLcdMode.values()) {
                if (mode.equals(lcdMode.name)) {
                    // Copy all args but the first into a new array to be passed to the mode
                    final String[] modeArgs = new String[args.length - 1]; // args.length >= 1
                    System.arraycopy(args, 1, modeArgs, 0, args.length - 1);

                    CaseControl.data().setLcdMode(lcdMode);
                    CaseControl.restartLcdTimer(modeArgs); // Restart the timer for the LCD mode
                    System.out.printf("Case LED mode set to %s\n", lcdMode.name);
                    return true; // Succesfully completed
                }
            }
            System.out.printf("Invalid mode: %s\n", mode);
        }
        return false;
    }
}
