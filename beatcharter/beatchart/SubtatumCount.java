package beatchart;

import java.util.Collections;
import java.util.Comparator;

public class SubtatumCount {
    public float start;
    public float mid;
    public float range;
    public float end;
    public int count;

    public SubtatumCount(float iStart, float iRange) {
        start = iStart;
        range = iRange;
        end = start + range;
        mid = start + (range / 2);
        count = 1;
    }

    public static class SortSubtatumCount implements Comparator<SubtatumCount> {
        public int compare(SubtatumCount c1, SubtatumCount c2) {
            if (c1.start == c2.start) {
                return 0;
            }
            return c1.start < c2.start ? -1 : 1;
        }
    }
}
