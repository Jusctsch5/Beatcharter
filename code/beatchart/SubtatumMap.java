package beatchart;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class SubtatumMap {
    public List<SubtatumCount> subtatumHashList;
    public List<SubtatumCount> collapsedSubtatumHashList;

    private float allowedRange = 1.0f;
    private float commonRangeMin = 80.0f;
    private float commonRangeMax = 200.0f;

    public SubtatumMap() {
        subtatumHashList = new ArrayList();
        collapsedSubtatumHashList = new ArrayList();
    }

    public SubtatumCount GetMostCommonSubtatumInCommonRange() {
        SubtatumCount defaultSubtatum = new SubtatumCount(0, 0);
        SubtatumCount mostCommonSubtatum = defaultSubtatum;
        for (SubtatumCount subtatumCount : subtatumHashList) {
            if ((subtatumCount.mid > commonRangeMin) &&
                    (subtatumCount.mid < commonRangeMax) &&
                    (subtatumCount.count > mostCommonSubtatum.count)) {
                mostCommonSubtatum = subtatumCount;
            }
        }
        return mostCommonSubtatum;
    }

    public SubtatumCount GetMostCommonSubtatumInCollapsedMap() {
        SubtatumCount defaultSubtatum = new SubtatumCount(0, 0);
        SubtatumCount mostCommonSubtatum = defaultSubtatum;
        for (SubtatumCount subtatumCount : collapsedSubtatumHashList) {
            if (subtatumCount.count > mostCommonSubtatum.count) {
                mostCommonSubtatum = subtatumCount;

            }
        }
        return mostCommonSubtatum;
    }


    public String SubtatumMapToString() {
        String map = "HashList:\n";
        for (SubtatumCount subtatumCount : subtatumHashList) {
            map += "start:" + subtatumCount.start + " end:" + subtatumCount.end + " count:" + subtatumCount.count + '\n';
        }

        map += " CollapsedHashList:\n";
        for (SubtatumCount subtatumCount : collapsedSubtatumHashList) {
            map += "start:" + subtatumCount.start + " end:" + subtatumCount.end + " count:" + subtatumCount.count + '\n';
        }
        return map;
    }

    public void AddSubtatumToMap(float isubtatum) {
        if (isubtatum == Float.POSITIVE_INFINITY) { return; }
        AddToSubtatumMap(isubtatum);
        AddToCollapsedSubtatumMap(isubtatum);
    }

    private void AddToSubtatumMap(float isubtatum) {
        for (SubtatumCount subtatumCount : subtatumHashList) {
            if ((isubtatum >= subtatumCount.start) && (isubtatum <= subtatumCount.end)) {
                subtatumCount.count += 1;
                return;
            }
        }

        SubtatumCount count = new SubtatumCount(isubtatum - allowedRange, allowedRange * 2);
        subtatumHashList.add(count);
        Collections.sort(subtatumHashList, new SubtatumCount.SortSubtatumCount());
    }

    private boolean IsSubtatumInCommonRange(float isubtatum) {
        if ((isubtatum >= commonRangeMin) && (isubtatum <= commonRangeMax)) {
            return true;
        }
        return false;
    }

    private float ConvertSubtatumToCommonRange(float isubtatum) {
        /* Subtatum may lie outside of common range. Use powers of two until it lies in the common range of subtatum, and return that subtatum
         *  Ex: subtatum of 860 lies outside of range.
         *  860 / 2 = 430, lies outside of range
         *  430 /2 = 215, lies outside of common range
         *  215 / 2 = 107.5 lies within common range
         */
        if (IsSubtatumInCommonRange(isubtatum)) {
            return isubtatum;
        }

        while (isubtatum < commonRangeMin) {
            isubtatum *= 2;
        }

        while (isubtatum > commonRangeMax) {
            isubtatum /= 2;
        }

        return isubtatum;
    }

    private void AddToCollapsedSubtatumMap(float isubtatum) {
        isubtatum = ConvertSubtatumToCommonRange(isubtatum);
        for (SubtatumCount subtatumCount : collapsedSubtatumHashList) {
            if ((isubtatum >= subtatumCount.start) && (isubtatum <= subtatumCount.end)) {
                subtatumCount.count += 1;
                return;
            }
        }

        SubtatumCount count = new SubtatumCount(isubtatum - allowedRange, allowedRange * 2);
        collapsedSubtatumHashList.add(count);
        Collections.sort(collapsedSubtatumHashList, new SubtatumCount.SortSubtatumCount());
    }
}