import { getAllContests } from "@/lib/contests";
import CompletedContestPage from "./CompletedContestPage";

export default function Completed() {
  const contests = getAllContests();
  return <CompletedContestPage contests={contests} />;
}
