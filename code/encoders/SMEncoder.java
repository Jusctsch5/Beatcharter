package encoders;/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 *
 */
public class SMEncoder extends Encoder {

    private static String Header =
            "#TITLE:$TITLE;\n" +
            "#SUBTITLE:;\n" +
            "#ARTIST:;\n" +
            "#TITLETRANSLIT:;\n" +
            "#SUBTITLETRANSLIT:;\n" +
            "#ARTISTTRANSLIT:;\n" +
            "#GENRE:;\n" +
            "#CREDIT:AutoStepper by phr00t.com;\n" +
            "#BANNER:$BGIMAGE;\n" +
            "#BACKGROUND:$BGIMAGE;\n" +
            "#LYRICSPATH:;\n" +
            "#CDTITLE:;\n" +
            "#MUSIC:$MUSICFILE;\n" +
            "#OFFSET:$STARTTIME;\n" +
            "#SAMPLESTART:30.0;\n" +
            "#SAMPLELENGTH:30.0;\n" +
            "#SELECTABLE:YES;\n" +
            "#BPMS:0.000000=$BPM;\n" +
            "#STOPS:;\n" +
            "#KEYSOUNDS:;\n" +
            "#ATTACKS:;";

    public static String Beginner =
            "Beginner:\n" +
            "     2:";
    public static String Easy =
            "Easy:\n" +
            "     4:";
    public static String Medium =
            "Medium:\n" +
            "     6:";
    public static String Hard =
            "Hard:\n" +
            "     8:";
    public static String Challenge =
            "Challenge:\n" +
            "     10:";

    private static String ChartHeader =
            "//---------------dance-single - ----------------\n" +
            "#NOTES:\n" +
            "     dance-single:\n" +
            "     :\n" +
            "     $DIFFICULTY\n" +
            "     0.733800,0.772920,0.048611,0.850698,0.060764,634.000000,628.000000,6.000000,105.000000,8.000000,0.000000,0.733800,0.772920,0.048611,0.850698,0.060764,634.000000,628.000000,6.000000,105.000000,8.000000,0.000000:\n" +
            "$NOTES\n" +
            ";\n\n";

    private static void copyFileUsingStream(File source, File dest) throws IOException {
        InputStream is = null;
        OutputStream os = null;
        try {
            is = new FileInputStream(source);
            os = new FileOutputStream(dest);
            byte[] buffer = new byte[1024];
            int length;
            while ((length = is.read(buffer)) > 0) {
                os.write(buffer, 0, length);
            }
        } finally {
            is.close();
            os.close();
        }
    }

    public static void AddNotes(BufferedWriter smfile, String difficulty, String notes) {
        try {
            smfile.write(ChartHeader.replace("$DIFFICULTY", difficulty).replace("$NOTES", notes));
        } catch(Exception e) { }
    }

    public static void Complete(BufferedWriter smfile) {
        try {
            smfile.close();
        } catch(Exception e) { }
    }

    public static File getSMFile(File songFile, String outputdir) {
        String filename = songFile.getName();
        File dir = new File(outputdir, filename + "_dir/");
        return new File(dir, filename + ".sm");
    }

    /**

     * @param bpm Beats per minute of the song
     * @param startTime start time of the song
     * @return BufferedWriter This returns sum of numA and numB.
     */
    public static BufferedWriter GenerateSM(float bpm, float startTime, File songFile, String outputDir) {
        String fileName = songFile.getName();
        String songName = FilenameUtils.removeExtension(fileName);
        String shortName = songName.length() > 32 ? songName.substring(0, 32) : songName;
        File dir = new File(outputDir, fileName + "/");
        dir.mkdirs();
        File smFile = new File(dir, fileName + ".sm");

        try {
            // Remove old file and create new file
            smFile.delete();
            FileUtils.copyFile(songFile,  new File(dir, fileName));
            BufferedWriter writer = new BufferedWriter(new FileWriter(smFile));
            writer.write(Header.replace("$TITLE", shortName)
                         .replace("$MUSICFILE", fileName)
                         .replace("$STARTTIME", Float.toString(startTime)) // .replace("$STARTTIME", Float.toString(startTime + AutoStepper.STARTSYNC))
                         .replace("$BPM", Float.toString(bpm)));
            return writer;
        } catch(Exception e) {}
        return null;
    }
}
