import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export function utcDate(date: string | number | Date | dayjs.Dayjs): dayjs.Dayjs {
  return dayjs.utc(date);
}

export function relativeDate(date: string | number | Date | dayjs.Dayjs): string {
  const localDate = utcDate(date);
  if (dayjs().diff(localDate, "month") > 0) {
    return localDate.format("MMMM D, YYYY");
  }
  return localDate.fromNow();
}
