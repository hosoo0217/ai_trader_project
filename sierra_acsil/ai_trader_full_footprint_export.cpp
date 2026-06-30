// AI Trader Full Footprint Exporter for Sierra Chart ACSIL
//
// Purpose:
//   Export loaded chart Volume-at-Price data to a private CSV file for
//   AI Trader Order Flow research validation.
//
// Safety:
//   This custom study is data export only. It does not place orders, submit
//   trades, connect to brokers, connect to MT5, call external APIs, or modify
//   strategy logic.
//
// Install/build notes:
//   1. Copy this file into Sierra Chart's ACS_Source folder.
//   2. In Sierra Chart, open Analysis > Build Custom Studies DLL.
//   3. Select this file and build it.
//   4. Add "AI Trader Full Footprint CSV Exporter" to a chart that has
//      Volume-at-Price data available.
//   5. Set "Export Now" to Yes, then apply the study settings.
//
// Expected ACSIL members used:
//   - sc.MaintainVolumeAtPriceData
//   - sc.VolumeAtPriceForBars
//   - GetSizeAtBarIndex
//   - GetVAPElementAtIndex
//   - sc.TickSize
//   - sc.BaseDateTimeIn

#include "sierrachart.h"

#include <fstream>

SCDLLName("AI Trader Full Footprint Exporter")

namespace
{
const char* const kExportPath =
    "C:\\Users\\hosoo\\Desktop\\ai_trader_project\\private_data\\sierra_chart\\gc_full_footprint_acsil_export.csv";

SCString DateTimeToText(SCStudyInterfaceRef sc, const SCDateTime& dateTime)
{
    // Sierra Chart ACSIL commonly supports sc.FormatDateTime for chart
    // timestamps. If a local Sierra build names this differently, replace this
    // helper with the equivalent date-time formatting call from that build.
    return sc.FormatDateTime(dateTime);
}
}  // namespace

SCSFExport scsf_AiTraderFullFootprintCSVExporter(SCStudyInterfaceRef sc)
{
    SCInputRef ExportNow = sc.Input[0];

    if (sc.SetDefaults)
    {
        sc.GraphName = "AI Trader Full Footprint CSV Exporter";
        sc.StudyDescription =
            "Exports loaded chart Volume-at-Price rows to a private CSV file for "
            "AI Trader Order Flow validation. Data export only; no trading logic.";
        sc.AutoLoop = 0;
        sc.GraphRegion = 0;
        sc.MaintainVolumeAtPriceData = 1;

        ExportNow.Name = "Export Now";
        ExportNow.SetYesNo(false);

        return;
    }

    // Keep Volume-at-Price data maintained after defaults are applied.
    sc.MaintainVolumeAtPriceData = 1;

    if (!ExportNow.GetYesNo())
        return;

    if (sc.VolumeAtPriceForBars == nullptr)
    {
        sc.AddMessageToLog(
            "AI Trader footprint export skipped: VolumeAtPriceForBars is not available on this chart.",
            1);
        return;
    }

    std::ofstream output(kExportPath, std::ios::out | std::ios::trunc);
    if (!output.is_open())
    {
        SCString message;
        message.Format("AI Trader footprint export failed: could not open %s", kExportPath);
        sc.AddMessageToLog(message, 1);
        return;
    }

    output << "DateTime,BarIndex,Price,BidVolume,AskVolume,TotalVolume,Delta,NumTrades\n";

    int exportedRows = 0;
    int exportedBars = 0;

    for (int barIndex = 0; barIndex < sc.ArraySize; ++barIndex)
    {
        const int priceLevelCount = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(barIndex);
        if (priceLevelCount <= 0)
            continue;

        ++exportedBars;

        const SCString dateTimeText = DateTimeToText(sc, sc.BaseDateTimeIn[barIndex]);

        for (int vapIndex = 0; vapIndex < priceLevelCount; ++vapIndex)
        {
            const s_VolumeAtPriceV2* vapElement = nullptr;
            const bool found = sc.VolumeAtPriceForBars->GetVAPElementAtIndex(
                barIndex,
                vapIndex,
                &vapElement);

            if (!found || vapElement == nullptr)
                continue;

            const double price = static_cast<double>(vapElement->PriceInTicks) * sc.TickSize;
            const int bidVolume = static_cast<int>(vapElement->BidVolume);
            const int askVolume = static_cast<int>(vapElement->AskVolume);
            const int totalVolume = static_cast<int>(vapElement->Volume);
            const int delta = askVolume - bidVolume;

            // Sierra Chart versions commonly expose NumberOfTrades on
            // s_VolumeAtPriceV2. If this member is unavailable in a local build,
            // replace it with the equivalent ACSIL trade-count field or set 0.
            const int numTrades = static_cast<int>(vapElement->NumberOfTrades);

            output << dateTimeText.GetChars() << ','
                   << barIndex << ','
                   << price << ','
                   << bidVolume << ','
                   << askVolume << ','
                   << totalVolume << ','
                   << delta << ','
                   << numTrades << '\n';

            ++exportedRows;
        }
    }

    output.close();

    SCString message;
    message.Format(
        "AI Trader footprint export complete: %d rows across %d bars written to %s",
        exportedRows,
        exportedBars,
        kExportPath);
    sc.AddMessageToLog(message, 0);
}
